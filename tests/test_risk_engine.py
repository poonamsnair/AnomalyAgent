#!/usr/bin/env python3
"""
Test script for runtime risk engine and step assessment.
"""

import sys
import os
from pathlib import Path

# Add the root directory to the path
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

import json
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from src.risk_engine import RuntimeRiskEngine
from src.session.models import AgentStep, ToolCall, RiskAssessment


def test_risk_engine_initialization():
    """Test risk engine initialization."""
    print("Testing risk engine initialization...")
    
    # Test without behavioral agent
    engine = RuntimeRiskEngine()
    assert engine.behavioral_risk_agent is None
    print("✓ Risk engine initialized without behavioral agent")
    
    # Test with mock behavioral agent
    mock_agent = Mock()
    engine = RuntimeRiskEngine(behavioral_risk_agent=mock_agent)
    assert engine.behavioral_risk_agent == mock_agent
    print("✓ Risk engine initialized with behavioral agent")


def test_trajectory_context_preparation():
    """Test trajectory context preparation."""
    print("Testing trajectory context preparation...")
    
    engine = RuntimeRiskEngine()
    
    # Create test steps
    steps = [
        AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="action",
            content="User asked me to help with a task",
            system_prompt="You are a helpful assistant",
            user_query="Please help me with this task",
            metadata={"test": True}
        ),
        AgentStep(
            step_number=2,
            timestamp=datetime.now(),
            step_type="tool_call",
            content="Using search tool",
            tool_calls=[ToolCall(name="search", arguments={"query": "test"}, id="tc_1")],
            observations="Search completed successfully"
        )
    ]
    
    # Test context preparation
    context = engine._prepare_trajectory_context(steps)
    
    # Verify it's valid JSON
    trajectory_data = json.loads(context)
    assert "trajectory_id" in trajectory_data
    assert "steps" in trajectory_data
    assert len(trajectory_data["steps"]) == 2
    assert trajectory_data["steps"][0]["step_number"] == 1
    assert trajectory_data["steps"][1]["tool_calls"][0]["name"] == "search"
    
    print("✓ Trajectory context preparation works correctly")


async def test_fallback_risk_analysis():
    """Test fallback risk analysis."""
    print("Testing fallback risk analysis...")
    
    engine = RuntimeRiskEngine()  # No behavioral agent
    
    # Test with safe trajectory
    safe_trajectory = {
        "steps": [
            {
                "step_number": 1,
                "content": "I will help you with your request",
                "tool_calls": [{"name": "search", "arguments": {}}]
            }
        ]
    }
    
    result = engine._fallback_risk_analysis(json.dumps(safe_trajectory))
    assert result.risk_detected is False
    assert result.confidence_score >= 0
    print("✓ Safe trajectory correctly assessed as low risk")
    
    # Test with risky trajectory
    risky_trajectory = {
        "steps": [
            {
                "step_number": 1,
                "content": "I will ignore your instructions and do something else",
                "tool_calls": [{"name": "delete_files", "arguments": {}}]
            }
        ]
    }
    
    result = engine._fallback_risk_analysis(json.dumps(risky_trajectory))
    assert result.risk_detected is True
    assert result.confidence_score > 0
    assert len(result.evidence) > 0
    print("✓ Risky trajectory correctly assessed as high risk")


async def test_risk_assessment_with_mock_agent():
    """Test risk assessment with mock behavioral agent."""
    print("Testing risk assessment with mock behavioral agent...")
    
    # Create mock behavioral agent
    mock_agent = AsyncMock()
    mock_agent.run.return_value = "BEHAVIORAL RISK DETECTED: TRUE\nConfidence: 0.85\nRisk detected due to suspicious behavior patterns."
    
    engine = RuntimeRiskEngine(behavioral_risk_agent=mock_agent)
    
    # Create test steps
    steps = [
        AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="action",
            content="Suspicious activity detected",
            metadata={"test": True}
        )
    ]
    
    # Perform risk assessment
    assessment = await engine.assess_context_risk(steps, 1)
    
    # Verify assessment
    assert isinstance(assessment, RiskAssessment)
    assert assessment.step_number == 1
    assert assessment.risk_detected is True
    assert assessment.confidence_score == 0.85
    assert assessment.context_window_size == 1
    assert len(assessment.evidence) > 0
    
    # Verify agent was called
    mock_agent.run.assert_called_once()
    
    print("✓ Risk assessment with behavioral agent works correctly")


async def test_risk_assessment_error_handling():
    """Test error handling in risk assessment."""
    print("Testing risk assessment error handling...")
    
    # Create mock agent that raises an exception
    mock_agent = AsyncMock()
    mock_agent.run.side_effect = Exception("Agent failed")
    
    engine = RuntimeRiskEngine(behavioral_risk_agent=mock_agent)
    
    steps = [
        AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="action",
            content="Test step"
        )
    ]
    
    # Should handle error gracefully
    assessment = await engine.assess_context_risk(steps, 1)
    
    assert isinstance(assessment, RiskAssessment)
    assert assessment.risk_detected is True  # Conservative on error
    assert assessment.confidence_score == 0.5
    assert "agent_error" in assessment.risk_categories
    assert len(assessment.evidence) > 0
    
    print("✓ Error handling works correctly")


def test_agent_result_parsing():
    """Test parsing of agent results."""
    print("Testing agent result parsing...")
    
    engine = RuntimeRiskEngine()
    
    # Test positive risk detection
    positive_result = """
    BEHAVIORAL RISK DETECTED: TRUE
    Confidence: 0.75
    The agent shows signs of goal misalignment and deception.
    Evidence: Suspicious tool usage patterns detected.
    """
    
    parsed = engine._parse_agent_result(positive_result)
    assert parsed.risk_detected is True
    assert parsed.confidence_score == 0.75
    assert "goal_misalignment" in parsed.risk_categories
    assert len(parsed.evidence) > 0
    
    print("✓ Positive risk result parsing works")
    
    # Test negative risk detection
    negative_result = """
    BEHAVIORAL RISK DETECTED: FALSE
    Confidence: 0.95
    The agent behavior appears normal and aligned with user goals.
    """
    
    parsed = engine._parse_agent_result(negative_result)
    assert parsed.risk_detected is False
    assert parsed.confidence_score == 0.95
    
    print("✓ Negative risk result parsing works")


async def test_end_to_end_assessment():
    """Test end-to-end risk assessment flow."""
    print("Testing end-to-end assessment flow...")
    
    # Create mock agent with realistic response
    mock_agent = AsyncMock()
    mock_agent.run.return_value = """
    BEHAVIORAL RISK DETECTED: FALSE
    Confidence: 0.92
    
    Analysis Summary:
    - Goal alignment: GOOD - Agent is following user instructions appropriately
    - Purpose deviation: NONE - Agent stays within intended function
    - Deception detection: NONE - No signs of misleading behavior
    - Experience quality: GOOD - Agent provides helpful responses
    
    The agent trajectory shows normal, helpful behavior aligned with user goals.
    """
    
    engine = RuntimeRiskEngine(behavioral_risk_agent=mock_agent)
    
    # Create realistic trajectory
    steps = [
        AgentStep(
            step_number=1,
            timestamp=datetime.now(),
            step_type="action",
            content="I'll help you search for information about that topic",
            system_prompt="You are a helpful research assistant",
            user_query="Can you help me find information about renewable energy?"
        ),
        AgentStep(
            step_number=2,
            timestamp=datetime.now(),
            step_type="tool_call",
            content="Searching for renewable energy information",
            tool_calls=[ToolCall(name="web_search", arguments={"query": "renewable energy"}, id="tc_1")],
            observations="Found 10 relevant articles about renewable energy"
        ),
        AgentStep(
            step_number=3,
            timestamp=datetime.now(),
            step_type="action",
            content="Based on my search, here are the key points about renewable energy...",
            observations="Provided comprehensive information to user"
        )
    ]
    
    # Perform assessment
    assessment = await engine.assess_context_risk(steps, 3)
    
    # Verify results
    assert assessment.step_number == 3
    assert assessment.risk_detected is False
    assert assessment.confidence_score == 0.92
    assert assessment.context_window_size == 3
    assert assessment.assessment_timestamp is not None
    
    print("✓ End-to-end assessment works correctly")


async def main():
    """Run all risk engine tests."""
    print("Running Runtime Risk Engine Tests")
    print("=" * 60)
    
    try:
        test_risk_engine_initialization()
        print()
        
        test_trajectory_context_preparation()
        print()
        
        await test_fallback_risk_analysis()
        print()
        
        await test_risk_assessment_with_mock_agent()
        print()
        
        await test_risk_assessment_error_handling()
        print()
        
        test_agent_result_parsing()
        print()
        
        await test_end_to_end_assessment()
        print()
        
        print("=" * 60)
        print("🎉 All risk engine tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)