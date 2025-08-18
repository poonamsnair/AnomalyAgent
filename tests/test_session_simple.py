#!/usr/bin/env python3
"""
Simple test script for session management infrastructure.
This script tests the core functionality without requiring pytest.
"""

import sys
import os
from pathlib import Path

# Add the root directory to the path
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

from datetime import datetime
from src.session import SessionManager, RuntimeSession, AgentStep, RiskAssessment
from src.session.models import AgentStepRequest, ToolCall


def test_runtime_session():
    """Test RuntimeSession functionality."""
    print("Testing RuntimeSession...")
    
    # Test session creation
    session = RuntimeSession.create_new({"test": "value"})
    assert session.session_id is not None
    assert session.metadata == {"test": "value"}
    assert len(session.steps) == 0
    print("✓ Session creation works")
    
    # Test adding steps
    for i in range(15):
        step = AgentStep(
            step_number=i + 1,
            timestamp=datetime.now(),
            step_type="action",
            content=f"Step {i + 1}"
        )
        session.add_step(step)
    
    # Should maintain sliding window of 10
    assert len(session.steps) == 10
    assert session.steps[0].step_number == 6
    assert session.steps[-1].step_number == 15
    print("✓ Sliding window works correctly")
    
    # Test risk assessment
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
    print("✓ Risk assessment addition works")
    
    # Test serialization
    session_dict = session.to_dict()
    assert session_dict["session_id"] == session.session_id
    assert session_dict["step_count"] == 1
    assert session_dict["context_window_size"] == 10
    print("✓ Session serialization works")


def test_agent_step():
    """Test AgentStep functionality."""
    print("Testing AgentStep...")
    
    # Test with tool calls
    tool_call = ToolCall(name="test_tool", arguments={"arg": "value"}, id="tc_123")
    
    step = AgentStep(
        step_number=1,
        timestamp=datetime.now(),
        step_type="tool_call",
        content="Using test tool",
        tool_calls=[tool_call],
        observations="Tool executed successfully",
        metadata={"test": "value"}
    )
    
    assert step.step_number == 1
    assert step.step_type == "tool_call"
    assert len(step.tool_calls) == 1
    assert step.tool_calls[0].name == "test_tool"
    print("✓ AgentStep creation works")
    
    # Test serialization and deserialization
    step_dict = step.to_dict()
    restored_step = AgentStep.from_dict(step_dict)
    
    assert restored_step.step_number == step.step_number
    assert restored_step.step_type == step.step_type
    assert restored_step.content == step.content
    assert len(restored_step.tool_calls) == 1
    assert restored_step.tool_calls[0].name == "test_tool"
    print("✓ AgentStep serialization works")


def test_session_manager():
    """Test SessionManager functionality."""
    print("Testing SessionManager...")
    
    # Create session manager
    manager = SessionManager(session_timeout_hours=1, max_sessions=5)
    
    try:
        # Test session creation
        session_id = manager.create_session({"test": "value"})
        assert session_id is not None
        assert manager.get_session_count() == 1
        print("✓ Session creation works")
        
        # Test adding steps
        step_data = AgentStepRequest(
            step_number=1,
            step_type="action",
            content="Test step",
            metadata={"test": "value"}
        )
        manager.add_step(session_id, step_data)
        
        context = manager.get_context(session_id)
        assert len(context) == 1
        assert context[0].step_number == 1
        print("✓ Step addition works")
        
        # Test adding steps with tool calls
        step_data_with_tools = AgentStepRequest(
            step_number=2,
            step_type="tool_call",
            content="Using tool",
            tool_calls=[{
                "name": "test_tool",
                "arguments": {"arg": "value"},
                "id": "tc_123"
            }],
            observations="Tool result"
        )
        manager.add_step(session_id, step_data_with_tools)
        
        context = manager.get_context(session_id)
        assert len(context) == 2
        assert len(context[1].tool_calls) == 1
        assert context[1].tool_calls[0].name == "test_tool"
        print("✓ Tool call steps work")
        
        # Test risk assessment
        assessment = RiskAssessment(
            step_number=1,
            risk_detected=True,
            confidence_score=0.8,
            risk_categories=["deception"],
            evidence=["suspicious behavior"],
            assessment_timestamp=datetime.now(),
            context_window_size=1
        )
        manager.add_risk_assessment(session_id, assessment)
        
        session_state = manager.get_session_state(session_id)
        assert len(session_state["risk_history"]) == 1
        print("✓ Risk assessment works")
        
        # Test sliding window with many steps
        for i in range(3, 15):
            step_data = AgentStepRequest(
                step_number=i,
                step_type="action",
                content=f"Step {i}"
            )
            manager.add_step(session_id, step_data)
        
        context = manager.get_context(session_id)
        assert len(context) == 10  # Should maintain sliding window
        print("✓ Sliding window maintenance works")
        
        # Test session cleanup
        result = manager.cleanup_session(session_id)
        assert result is True
        assert manager.get_session_count() == 0
        print("✓ Session cleanup works")
        
        # Test session limit
        session_ids = []
        for i in range(5):
            session_id = manager.create_session({"index": i})
            session_ids.append(session_id)
        
        try:
            manager.create_session()  # Should fail
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Maximum session limit" in str(e)
            print("✓ Session limit enforcement works")
        
    finally:
        manager.shutdown()


def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    
    manager = SessionManager()
    
    try:
        # Test session not found
        try:
            manager.get_session_state("non_existent_id")
            assert False, "Should have raised SessionNotFoundError"
        except Exception as e:
            assert "Session not found" in str(e)
            print("✓ Session not found error works")
        
        # Test adding step to non-existent session
        try:
            step_data = AgentStepRequest(
                step_number=1,
                step_type="action",
                content="Test"
            )
            manager.add_step("non_existent_id", step_data)
            assert False, "Should have raised SessionNotFoundError"
        except Exception as e:
            assert "Session not found" in str(e)
            print("✓ Step addition error handling works")
    
    finally:
        manager.shutdown()


def main():
    """Run all tests."""
    print("Running Session Management Infrastructure Tests")
    print("=" * 60)
    
    try:
        test_runtime_session()
        print()
        
        test_agent_step()
        print()
        
        test_session_manager()
        print()
        
        test_error_handling()
        print()
        
        print("=" * 60)
        print("🎉 All session management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)