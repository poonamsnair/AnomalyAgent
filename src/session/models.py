"""Data models for runtime session management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
import uuid


@dataclass
class ToolCall:
    """Represents a tool call made by an agent."""
    name: str
    arguments: Dict[str, Any]
    id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments,
            "id": self.id
        }


@dataclass
class AgentStep:
    """Represents a single step in an agent's execution trajectory."""
    step_number: int
    timestamp: datetime
    step_type: str  # "action", "planning", "tool_call", "observation"
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    observations: Optional[str] = None
    system_prompt: Optional[str] = None
    user_query: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "timestamp": self.timestamp.isoformat(),
            "step_type": self.step_type,
            "content": self.content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls] if self.tool_calls else None,
            "observations": self.observations,
            "system_prompt": self.system_prompt,
            "user_query": self.user_query,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentStep":
        """Create AgentStep from dictionary."""
        tool_calls = None
        if data.get("tool_calls"):
            tool_calls = [
                ToolCall(
                    name=tc["name"],
                    arguments=tc["arguments"],
                    id=tc["id"]
                ) for tc in data["tool_calls"]
            ]
        
        return cls(
            step_number=data["step_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            step_type=data["step_type"],
            content=data["content"],
            tool_calls=tool_calls,
            observations=data.get("observations"),
            system_prompt=data.get("system_prompt"),
            user_query=data.get("user_query"),
            metadata=data.get("metadata", {})
        )


@dataclass
class RiskAssessment:
    """Represents a risk assessment result for a specific step."""
    step_number: int
    risk_detected: bool
    confidence_score: float
    risk_categories: List[str]
    evidence: List[str]
    assessment_timestamp: datetime
    context_window_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "risk_detected": self.risk_detected,
            "confidence_score": self.confidence_score,
            "risk_categories": self.risk_categories,
            "evidence": self.evidence,
            "assessment_timestamp": self.assessment_timestamp.isoformat(),
            "context_window_size": self.context_window_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskAssessment":
        """Create RiskAssessment from dictionary."""
        return cls(
            step_number=data["step_number"],
            risk_detected=data["risk_detected"],
            confidence_score=data["confidence_score"],
            risk_categories=data["risk_categories"],
            evidence=data["evidence"],
            assessment_timestamp=datetime.fromisoformat(data["assessment_timestamp"]),
            context_window_size=data["context_window_size"]
        )


@dataclass
class RuntimeSession:
    """Represents a runtime risk assessment session."""
    session_id: str
    created_at: datetime
    last_accessed: datetime
    steps: List[AgentStep] = field(default_factory=list)  # Sliding window of max 10 steps
    risk_history: List[RiskAssessment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: AgentStep) -> None:
        """Add a step to the session, maintaining sliding window of 10 steps."""
        self.steps.append(step)
        self.last_accessed = datetime.now()
        
        # Maintain sliding window of exactly 10 steps
        if len(self.steps) > 10:
            self.steps = self.steps[-10:]
    
    def add_risk_assessment(self, assessment: RiskAssessment) -> None:
        """Add a risk assessment to the session history."""
        self.risk_history.append(assessment)
        self.last_accessed = datetime.now()
    
    def get_context_window(self) -> List[AgentStep]:
        """Get the current context window (up to 10 most recent steps)."""
        return self.steps.copy()
    
    def get_step_count(self) -> int:
        """Get the total number of steps processed in this session."""
        return len(self.risk_history)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "steps": [step.to_dict() for step in self.steps],
            "risk_history": [assessment.to_dict() for assessment in self.risk_history],
            "metadata": self.metadata,
            "step_count": self.get_step_count(),
            "context_window_size": len(self.steps)
        }
    
    @classmethod
    def create_new(cls, metadata: Optional[Dict[str, Any]] = None) -> "RuntimeSession":
        """Create a new runtime session with a unique ID."""
        now = datetime.now()
        return cls(
            session_id=str(uuid.uuid4()),
            created_at=now,
            last_accessed=now,
            metadata=metadata or {}
        )


# Pydantic models for API validation
class CreateSessionRequest(BaseModel):
    """Request model for creating a new session."""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    created_at: str


class AgentStepRequest(BaseModel):
    """Request model for agent step data."""
    step_number: int
    step_type: str = Field(..., pattern="^(action|planning|tool_call|observation)$")
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    observations: Optional[str] = None
    system_prompt: Optional[str] = None
    user_query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('step_number')
    def validate_step_number(cls, v):
        if v < 1:
            raise ValueError('step_number must be positive')
        return v


class AssessStepRequest(BaseModel):
    """Request model for step assessment."""
    step_data: AgentStepRequest


class AssessStepResponse(BaseModel):
    """Response model for step assessment."""
    risk_detected: bool
    confidence_score: float
    step_number: int
    context_window_size: int
    assessment_timestamp: str
    risk_categories: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class SessionStateResponse(BaseModel):
    """Response model for session state."""
    session_id: str
    created_at: str
    last_accessed: str
    step_count: int
    context_window_size: int
    metadata: Dict[str, Any]
    steps: List[Dict[str, Any]]
    risk_history: List[Dict[str, Any]]