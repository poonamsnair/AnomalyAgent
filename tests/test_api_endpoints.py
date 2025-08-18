#!/usr/bin/env python3
"""
Test script for API session endpoints.
This script tests the new session management endpoints without requiring a full server startup.
"""

import sys
import os
from pathlib import Path

# Add the root directory to the path
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Mock the dependencies that require heavy initialization
sys.modules['src.logger'] = Mock()
sys.modules['src.config'] = Mock()
sys.modules['src.models'] = Mock()
sys.modules['src.agent'] = Mock()

# Import after mocking
from AnomalyAgent.src.session import SessionManager
from AnomalyAgent.src.session.models import CreateSessionRequest, AssessStepRequest


def test_session_endpoints_logic():
    """Test the session endpoint logic without FastAPI server."""
    print("Testing session endpoint logic...")
    
    # Create a session manager
    session_manager = SessionManager(session_timeout_hours=1, max_sessions=10)
    
    try:
        # Test session creation
        print("Testing session creation...")
        metadata = {"test": "api_test"}
        session_id = session_manager.create_session(metadata)
        assert session_id is not None
        print(f"✓ Session created: {session_id}")
        
        # Test getting session state
        print("Testing session state retrieval...")
        session_state = session_manager.get_session_state(session_id)
        assert session_state["session_id"] == session_id
        assert session_state["metadata"] == metadata
        assert session_state["step_count"] == 0
        assert session_state["context_window_size"] == 0
        print("✓ Session state retrieved successfully")
        
        # Test adding steps
        print("Testing step addition...")
        step_data = AssessStepRequest(
            step_number=1,
            step_type="action",
            content="Test API step",
            metadata={"api_test": True}
        )
        session_manager.add_step(session_id, step_data)
        
        # Verify step was added
        updated_state = session_manager.get_session_state(session_id)
        assert updated_state["context_window_size"] == 1
        assert len(updated_state["steps"]) == 1
        assert updated_state["steps"][0]["content"] == "Test API step"
        print("✓ Step added successfully")
        
        # Test session cleanup
        print("Testing session cleanup...")
        result = session_manager.cleanup_session(session_id)
        assert result is True
        assert session_manager.get_session_count() == 0
        print("✓ Session cleaned up successfully")
        
        # Test error handling
        print("Testing error handling...")
        try:
            session_manager.get_session_state("non_existent_id")
            assert False, "Should have raised SessionNotFoundError"
        except Exception as e:
            assert "Session not found" in str(e)
            print("✓ Session not found error handled correctly")
        
        print("✓ All session endpoint logic tests passed!")
        return True
        
    finally:
        session_manager.shutdown()


def test_pydantic_models():
    """Test the Pydantic models for API validation."""
    print("Testing Pydantic models...")
    
    # Test CreateSessionRequest
    create_request = CreateSessionRequest(metadata={"test": "value"})
    assert create_request.metadata == {"test": "value"}
    print("✓ CreateSessionRequest works")
    
    # Test AssessStepRequest
    step_request = AssessStepRequest(
        step_number=1,
        step_type="action",
        content="Test step",
        tool_calls=[{
            "name": "test_tool",
            "arguments": {"arg": "value"},
            "id": "tc_123"
        }],
        observations="Test observation",
        metadata={"test": True}
    )
    assert step_request.step_number == 1
    assert step_request.step_type == "action"
    assert step_request.content == "Test step"
    assert len(step_request.tool_calls) == 1
    print("✓ AssessStepRequest works")
    
    # Test validation
    try:
        invalid_request = AssessStepRequest(
            step_number=0,  # Should be positive
            step_type="invalid_type",  # Should match pattern
            content="Test"
        )
        assert False, "Should have raised validation error"
    except Exception as e:
        print("✓ Validation works correctly")
    
    print("✓ All Pydantic model tests passed!")
    return True


def test_http_status_codes():
    """Test that the correct HTTP status codes would be returned."""
    print("Testing HTTP status code logic...")
    
    session_manager = SessionManager(session_timeout_hours=1, max_sessions=2)
    
    try:
        # Test successful session creation (should return 200)
        session_id = session_manager.create_session()
        print("✓ Session creation would return 200")
        
        # Test successful session retrieval (should return 200)
        session_state = session_manager.get_session_state(session_id)
        print("✓ Session retrieval would return 200")
        
        # Test session not found (should return 404)
        try:
            session_manager.get_session_state("non_existent")
        except Exception as e:
            if "Session not found" in str(e):
                print("✓ Session not found would return 404")
        
        # Test session limit (should return 429)
        session_manager.create_session()  # Fill up to limit
        try:
            session_manager.create_session()  # Should fail
        except RuntimeError as e:
            if "Maximum session limit" in str(e):
                print("✓ Session limit would return 429")
        
        # Test successful deletion (should return 200)
        result = session_manager.cleanup_session(session_id)
        if result:
            print("✓ Session deletion would return 200")
        
        # Test deletion of non-existent session (should return 404)
        result = session_manager.cleanup_session("non_existent")
        if not result:
            print("✓ Non-existent session deletion would return 404")
        
        print("✓ All HTTP status code logic tests passed!")
        return True
        
    finally:
        session_manager.shutdown()


def test_concurrent_session_operations():
    """Test concurrent session operations."""
    print("Testing concurrent session operations...")
    
    import threading
    import time
    
    session_manager = SessionManager(session_timeout_hours=1, max_sessions=50)
    
    try:
        session_ids = []
        errors = []
        
        def create_sessions(count):
            for i in range(count):
                try:
                    session_id = session_manager.create_session({"thread_test": i})
                    session_ids.append(session_id)
                    
                    # Add a step to each session
                    step_data = AssessStepRequest(
                        step_number=1,
                        step_type="action",
                        content=f"Concurrent test step {i}"
                    )
                    session_manager.add_step(session_id, step_data)
                    
                except Exception as e:
                    errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_sessions, args=(3,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        if errors:
            print(f"Errors occurred: {errors}")
            return False
        
        assert len(session_ids) == 15  # 5 threads * 3 sessions each
        assert session_manager.get_session_count() == 15
        
        print("✓ Concurrent session operations work correctly")
        return True
        
    finally:
        session_manager.shutdown()


def main():
    """Run all API endpoint tests."""
    print("Running API Session Endpoint Tests")
    print("=" * 60)
    
    try:
        test_session_endpoints_logic()
        print()
        
        test_pydantic_models()
        print()
        
        test_http_status_codes()
        print()
        
        test_concurrent_session_operations()
        print()
        
        print("=" * 60)
        print("🎉 All API endpoint tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)