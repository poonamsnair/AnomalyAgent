"""Thread-safe session manager for runtime risk assessment."""

import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

from .models import RuntimeSession, AgentStep, RiskAssessment, AgentStepRequest


class SessionNotFoundError(Exception):
    """Raised when a session is not found."""
    pass


class SessionExpiredError(Exception):
    """Raised when a session has expired."""
    pass


class InvalidStepDataError(Exception):
    """Raised when step data is invalid."""
    pass


class SessionManager:
    """Thread-safe manager for runtime assessment sessions."""
    
    def __init__(self, session_timeout_hours: int = 24, max_sessions: int = 1000):
        """
        Initialize the session manager.
        
        Args:
            session_timeout_hours: Hours after which inactive sessions expire
            max_sessions: Maximum number of concurrent sessions
        """
        self._sessions: Dict[str, RuntimeSession] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._session_timeout = timedelta(hours=session_timeout_hours)
        self._max_sessions = max_sessions
        self._cleanup_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="session-cleanup")
        self._logger = logging.getLogger(__name__)
        
        # Start periodic cleanup
        self._start_cleanup_timer()
    
    def create_session(self, metadata: Optional[Dict] = None) -> str:
        """
        Create a new assessment session.
        
        Args:
            metadata: Optional metadata to associate with the session
            
        Returns:
            str: The unique session ID
            
        Raises:
            RuntimeError: If maximum session limit is reached
        """
        with self._lock:
            # Check session limit
            if len(self._sessions) >= self._max_sessions:
                # Try cleanup first
                self._cleanup_expired_sessions()
                if len(self._sessions) >= self._max_sessions:
                    raise RuntimeError(f"Maximum session limit ({self._max_sessions}) reached")
            
            session = RuntimeSession.create_new(metadata)
            self._sessions[session.session_id] = session
            
            self._logger.info(f"Created new session: {session.session_id}")
            return session.session_id
    
    def add_step(self, session_id: str, step_data: AgentStepRequest) -> None:
        """
        Add a step to an existing session.
        
        Args:
            session_id: The session identifier
            step_data: The step data to add
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
            InvalidStepDataError: If step data is invalid
        """
        with self._lock:
            session = self._get_session(session_id)
            
            try:
                # Convert request model to AgentStep
                tool_calls = None
                if step_data.tool_calls:
                    from .models import ToolCall
                    tool_calls = [
                        ToolCall(
                            name=tc.get("name", ""),
                            arguments=tc.get("arguments", {}),
                            id=tc.get("id", "")
                        ) for tc in step_data.tool_calls
                    ]
                
                agent_step = AgentStep(
                    step_number=step_data.step_number,
                    timestamp=datetime.now(),
                    step_type=step_data.step_type,
                    content=step_data.content,
                    tool_calls=tool_calls,
                    observations=step_data.observations,
                    system_prompt=step_data.system_prompt,
                    user_query=step_data.user_query,
                    metadata=step_data.metadata or {}
                )
                
                session.add_step(agent_step)
                self._logger.debug(f"Added step {step_data.step_number} to session {session_id}")
                
            except Exception as e:
                raise InvalidStepDataError(f"Invalid step data: {str(e)}")
    
    def add_risk_assessment(self, session_id: str, assessment: RiskAssessment) -> None:
        """
        Add a risk assessment to a session.
        
        Args:
            session_id: The session identifier
            assessment: The risk assessment to add
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        with self._lock:
            session = self._get_session(session_id)
            session.add_risk_assessment(assessment)
            self._logger.debug(f"Added risk assessment for step {assessment.step_number} to session {session_id}")
    
    def get_context(self, session_id: str) -> List[AgentStep]:
        """
        Get the current context window for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            List[AgentStep]: The current context window (up to 10 steps)
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        with self._lock:
            session = self._get_session(session_id)
            return session.get_context_window()
    
    def get_session_state(self, session_id: str) -> Dict:
        """
        Get the complete state of a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dict: The session state as a dictionary
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        with self._lock:
            session = self._get_session(session_id)
            return session.to_dict()
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Remove a session and clean up its resources.
        
        Args:
            session_id: The session identifier
            
        Returns:
            bool: True if session was found and removed, False otherwise
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                self._logger.info(f"Cleaned up session: {session_id}")
                return True
            return False
    
    def list_sessions(self) -> List[str]:
        """
        Get a list of all active session IDs.
        
        Returns:
            List[str]: List of session IDs
        """
        with self._lock:
            return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """
        Get the number of active sessions.
        
        Returns:
            int: Number of active sessions
        """
        with self._lock:
            return len(self._sessions)
    
    def _get_session(self, session_id: str) -> RuntimeSession:
        """
        Get a session by ID, checking for expiration.
        
        Args:
            session_id: The session identifier
            
        Returns:
            RuntimeSession: The session object
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        
        session = self._sessions[session_id]
        
        # Check if session has expired
        if datetime.now() - session.last_accessed > self._session_timeout:
            del self._sessions[session_id]
            raise SessionExpiredError(f"Session expired: {session_id}")
        
        return session
    
    def _cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            int: Number of sessions cleaned up
        """
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if now - session.last_accessed > self._session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
            self._logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired_sessions)
    
    def _start_cleanup_timer(self) -> None:
        """Start periodic cleanup of expired sessions."""
        def cleanup_task():
            try:
                with self._lock:
                    cleaned_count = self._cleanup_expired_sessions()
                    if cleaned_count > 0:
                        self._logger.info(f"Periodic cleanup removed {cleaned_count} expired sessions")
            except Exception as e:
                self._logger.error(f"Error during periodic cleanup: {e}")
            
            # Schedule next cleanup in 1 hour
            threading.Timer(3600, cleanup_task).start()
        
        # Start first cleanup in 1 hour
        threading.Timer(3600, cleanup_task).start()
    
    def shutdown(self) -> None:
        """Shutdown the session manager and clean up resources."""
        with self._lock:
            self._cleanup_executor.shutdown(wait=True)
            self._sessions.clear()
            self._logger.info("Session manager shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()