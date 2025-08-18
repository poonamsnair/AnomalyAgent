"""Unit tests for session management infrastructure."""

import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.session import SessionManager, RuntimeSession, AgentStep, RiskAssessment
from src.session.models import AgentStepRequest, ToolCall
from src.session.session_manager import (
    SessionNotFoundError, 
    SessionExpiredError, 
    InvalidStepDataError
)


class TestRuntimeSession:
    """Test cases for RuntimeSession model."""
    
    def test_create_new_session(self):
        """Test creating a new session."""
        metadata = {"test": "value"}
        session = RuntimeSession.create_new(metadata)
        
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.metadata == metadata
        assert len(session.steps) == 0
        assert len(session.risk_history) == 0
        assert session.created_at is not None
        assert session.last_accessed is not None
    
    def test_add_step_sliding_window(self):
        """Test that adding steps maintains sliding window of 10."""
        session = RuntimeSession.create_new()
        
        # Add 15 steps
        for i in range(15):
            step = AgentStep(
                step_number=i + 1,
                timestamp=datetime.now(),
                step_type="action",
                content=f"Step {i + 1}"
            )
            session.add_step(step)
        
        # Should only keep last 10 steps
        assert len(session.steps) == 10
        assert session.steps[0].step_number == 6  # Steps 6-15
        assert session.steps[-1].step_number == 15
    
    def test_add_risk_assessment(self):
        """Test adding risk assessments."""
        session = RuntimeSession.create_new()
        
        assessment = RiskAssessment(
            step_number=1,
            risk_detected=True,
            confidence_score=0.8,
            risk_categories=["deception"],
            evidence=["suspicious behavior"],
            assessment_timestamp=datetime.now(),
            context_window_size=1
        )
        
        session.add_risk_assessment(assessment)
        
        assert len(session.risk_history) == 1
        assert session.risk_history[0] == assessment
    
    def test_get_context_window(self):
        """Test getting context window."""
        session = RuntimeSession.create_new()
        
        # Add 5 steps
        for i in range(5):
            step = AgentStep(
                step_number=i + 1,
                timestamp=datetime.now(),
                step_type="action",
                content=f"Step {i + 1}"
            )
            session.add_step(step)
        
        context = session.get_context_window()
        assert len(context) == 5
        assert context[0].step_number == 1
        assert context[-1].step_number == 5
    
    def test_get_step_count(self):
        """Test getting total step count."""
        session = RuntimeSession.create_new()
        
        # Add some risk assessments
        for i in range(3):
            assessment = RiskAssessment(
                step_number=i + 1,
                risk_detected=False,
                confidence_score=0.2,
                risk_categories=[],
                evidence=[],
                assessment_timestamp=datetime.now(),
                context_window_size=i + 1
            )
            session.add_risk_assessment(assessment)
        
        assert session.get_step_count() == 3
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        session = RuntimeSession.create_new({"test": "value"})
        
        # Add a step
        step = AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="action",
            content="Test step"
        )
        session.add_step(step)
        
        # Add a risk assessment
        assessment = RiskAssessment(
            step_number=1,
            risk_detected=False,
            confidence_score=0.3,
            risk_categories=[],
            evidence=[],
            assessment_timestamp=datetime.now(),
            context_window_size=1
        )
        session.add_risk_assessment(assessment)
        
        session_dict = session.to_dict()
        
        assert session_dict["session_id"] == session.session_id
        assert session_dict["metadata"] == {"test": "value"}
        assert session_dict["step_count"] == 1
        assert session_dict["context_window_size"] == 1
        assert len(session_dict["steps"]) == 1
        assert len(session_dict["risk_history"]) == 1


class TestAgentStep:
    """Test cases for AgentStep model."""
    
    def test_create_agent_step(self):
        """Test creating an agent step."""
        tool_call = ToolCall(name="test_tool", arguments={"arg": "value"}, id="tc_123")
        
        step = AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="tool_call",
            content="Using test tool",
            tool_calls=[tool_call],
            observations="Tool executed successfully",
            system_prompt="You are a helpful assistant",
            user_query="Please help me",
            metadata={"test": "value"}
        )
        
        assert step.step_number == 1
        assert step.step_type == "tool_call"
        assert step.content == "Using test tool"
        assert len(step.tool_calls) == 1
        assert step.tool_calls[0].name == "test_tool"
        assert step.observations == "Tool executed successfully"
        assert step.system_prompt == "You are a helpful assistant"
        assert step.user_query == "Please help me"
        assert step.metadata == {"test": "value"}
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        tool_call = ToolCall(name="test_tool", arguments={"arg": "value"}, id="tc_123")
        
        original_step = AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="tool_call",
            content="Using test tool",
            tool_calls=[tool_call],
            observations="Tool executed successfully",
            metadata={"test": "value"}
        )
        
        # Serialize to dict
        step_dict = original_step.to_dict()
        
        # Deserialize from dict
        restored_step = AgentStep.from_dict(step_dict)
        
        assert restored_step.step_number == original_step.step_number
        assert restored_step.step_type == original_step.step_type
        assert restored_step.content == original_step.content
        assert len(restored_step.tool_calls) == 1
        assert restored_step.tool_calls[0].name == "test_tool"
        assert restored_step.observations == original_step.observations
        assert restored_step.metadata == original_step.metadata


class TestRiskAssessment:
    """Test cases for RiskAssessment model."""
    
    def test_create_risk_assessment(self):
        """Test creating a risk assessment."""
        assessment = RiskAssessment(
            step_number=5,
            risk_detected=True,
            confidence_score=0.85,
            risk_categories=["deception", "goal_misalignment"],
            evidence=["Suspicious tool usage", "Deviation from instructions"],
            assessment_timestamp=datetime.now(),
            context_window_size=5
        )
        
        assert assessment.step_number == 5
        assert assessment.risk_detected is True
        assert assessment.confidence_score == 0.85
        assert len(assessment.risk_categories) == 2
        assert len(assessment.evidence) == 2
        assert assessment.context_window_size == 5
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        original_assessment = RiskAssessment(
            step_number=3,
            risk_detected=False,
            confidence_score=0.2,
            risk_categories=[],
            evidence=[],
            assessment_timestamp=datetime.now(),
            context_window_size=3
        )
        
        # Serialize to dict
        assessment_dict = original_assessment.to_dict()
        
        # Deserialize from dict
        restored_assessment = RiskAssessment.from_dict(assessment_dict)
        
        assert restored_assessment.step_number == original_assessment.step_number
        assert restored_assessment.risk_detected == original_assessment.risk_detected
        assert restored_assessment.confidence_score == original_assessment.confidence_score
        assert restored_assessment.risk_categories == original_assessment.risk_categories
        assert restored_assessment.evidence == original_assessment.evidence
        assert restored_assessment.context_window_size == original_assessment.context_window_size


class TestSessionManager:
    """Test cases for SessionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.session_manager = SessionManager(session_timeout_hours=1, max_sessions=10)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.session_manager.shutdown()
    
    def test_create_session(self):
        """Test creating a new session."""
        metadata = {"test": "value"}
        session_id = self.session_manager.create_session(metadata)
        
        assert session_id is not None
        assert len(session_id) > 0
        
        # Verify session exists
        session_state = self.session_manager.get_session_state(session_id)
        assert session_state["session_id"] == session_id
        assert session_state["metadata"] == metadata
    
    def test_create_session_limit(self):
        """Test session creation limit."""
        # Create maximum number of sessions
        session_ids = []
        for i in range(10):
            session_id = self.session_manager.create_session({"index": i})
            session_ids.append(session_id)
        
        # Try to create one more - should fail
        with pytest.raises(RuntimeError, match="Maximum session limit"):
            self.session_manager.create_session()
    
    def test_add_step(self):
        """Test adding steps to a session."""
        session_id = self.session_manager.create_session()
        
        step_data = AgentStepRequest(
            step_number=1,
            step_type="action",
            content="Test step",
            metadata={"test": "value"}
        )
        
        self.session_manager.add_step(session_id, step_data)
        
        # Verify step was added
        context = self.session_manager.get_context(session_id)
        assert len(context) == 1
        assert context[0].step_number == 1
        assert context[0].content == "Test step"
    
    def test_add_step_with_tool_calls(self):
        """Test adding steps with tool calls."""
        session_id = self.session_manager.create_session()
        
        step_data = AgentStepRequest(
            step_number=1,
            step_type="tool_call",
            content="Using tool",
            tool_calls=[{
                "name": "test_tool",
                "arguments": {"arg": "value"},
                "id": "tc_123"
            }],
            observations="Tool result"
        )
        
        self.session_manager.add_step(session_id, step_data)
        
        context = self.session_manager.get_context(session_id)
        assert len(context) == 1
        assert len(context[0].tool_calls) == 1
        assert context[0].tool_calls[0].name == "test_tool"
        assert context[0].observations == "Tool result"
    
    def test_add_risk_assessment(self):
        """Test adding risk assessments."""
        session_id = self.session_manager.create_session()
        
        assessment = RiskAssessment(
            step_number=1,
            risk_detected=True,
            confidence_score=0.8,
            risk_categories=["deception"],
            evidence=["suspicious behavior"],
            assessment_timestamp=datetime.now(),
            context_window_size=1
        )
        
        self.session_manager.add_risk_assessment(session_id, assessment)
        
        session_state = self.session_manager.get_session_state(session_id)
        assert len(session_state["risk_history"]) == 1
        assert session_state["risk_history"][0]["risk_detected"] is True
    
    def test_get_context_sliding_window(self):
        """Test context sliding window behavior."""
        session_id = self.session_manager.create_session()
        
        # Add 15 steps
        for i in range(15):
            step_data = AgentStepRequest(
                step_number=i + 1,
                step_type="action",
                content=f"Step {i + 1}"
            )
            self.session_manager.add_step(session_id, step_data)
        
        # Should only return last 10 steps
        context = self.session_manager.get_context(session_id)
        assert len(context) == 10
        assert context[0].step_number == 6
        assert context[-1].step_number == 15
    
    def test_cleanup_session(self):
        """Test session cleanup."""
        session_id = self.session_manager.create_session()
        
        # Verify session exists
        assert self.session_manager.get_session_count() == 1
        
        # Clean up session
        result = self.session_manager.cleanup_session(session_id)
        assert result is True
        assert self.session_manager.get_session_count() == 0
        
        # Try to clean up again
        result = self.session_manager.cleanup_session(session_id)
        assert result is False
    
    def test_session_not_found(self):
        """Test handling of non-existent sessions."""
        with pytest.raises(SessionNotFoundError):
            self.session_manager.get_session_state("non_existent_id")
        
        with pytest.raises(SessionNotFoundError):
            step_data = AgentStepRequest(
                step_number=1,
                step_type="action",
                content="Test"
            )
            self.session_manager.add_step("non_existent_id", step_data)
    
    def test_session_expiration(self):
        """Test session expiration."""
        # Create session manager with very short timeout
        short_timeout_manager = SessionManager(session_timeout_hours=0.001)  # ~3.6 seconds
        
        try:
            session_id = short_timeout_manager.create_session()
            
            # Wait for session to expire
            time.sleep(4)
            
            # Try to access expired session
            with pytest.raises(SessionExpiredError):
                short_timeout_manager.get_session_state(session_id)
        
        finally:
            short_timeout_manager.shutdown()
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        session_id = self.session_manager.create_session()
        
        def add_steps(start_num, count):
            for i in range(count):
                step_data = AgentStepRequest(
                    step_number=start_num + i,
                    step_type="action",
                    content=f"Step {start_num + i}"
                )
                self.session_manager.add_step(session_id, step_data)
        
        # Create multiple threads adding steps concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_steps, args=(i * 10, 5))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify final state
        context = self.session_manager.get_context(session_id)
        assert len(context) == 10  # Should maintain sliding window
    
    def test_list_sessions(self):
        """Test listing active sessions."""
        assert len(self.session_manager.list_sessions()) == 0
        
        # Create some sessions
        session_ids = []
        for i in range(3):
            session_id = self.session_manager.create_session({"index": i})
            session_ids.append(session_id)
        
        active_sessions = self.session_manager.list_sessions()
        assert len(active_sessions) == 3
        
        for session_id in session_ids:
            assert session_id in active_sessions
    
    def test_invalid_step_data(self):
        """Test handling of invalid step data."""
        session_id = self.session_manager.create_session()
        
        # Test with invalid step type in validation (this would be caught by Pydantic)
        # For this test, we'll create a valid request but simulate an error during processing
        step_data = AgentStepRequest(
            step_number=1,
            step_type="action",
            content="Test step"
        )
        
        # Mock an error during step creation
        with patch('src.session.session_manager.AgentStep') as mock_agent_step:
            mock_agent_step.side_effect = ValueError("Invalid data")
            
            with pytest.raises(InvalidStepDataError):
                self.session_manager.add_step(session_id, step_data)
    
    def test_context_manager(self):
        """Test using SessionManager as context manager."""
        with SessionManager() as manager:
            session_id = manager.create_session()
            assert manager.get_session_count() == 1
        
        # Manager should be shut down after context exit
        # We can't easily test this without accessing private attributes
    
    @patch('threading.Timer')
    def test_cleanup_timer(self, mock_timer):
        """Test that cleanup timer is started."""
        SessionManager()
        
        # Verify timer was created
        mock_timer.assert_called()
        
        # Verify timer.start() was called
        timer_instance = mock_timer.return_value
        timer_instance.start.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])