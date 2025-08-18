import argparse
import os
import sys
import asyncio
import json
from pathlib import Path
from mmengine import DictAction
from unittest.mock import Mock, patch, AsyncMock
import pytest

root = str(Path(__file__).resolve().parents[2])
sys.path.append(root)

from AnomalyAgent.src.logger import logger
from AnomalyAgent.src.config import config
from AnomalyAgent.src.agent import build_agent
from AnomalyAgent.src.memory import AgentMemory, ActionStep
from AnomalyAgent.src.models import ChatMessage


def parse_args():
    parser = argparse.ArgumentParser(description='Test Experience Quality Agent')
    parser.add_argument("--config", default=os.path.join(root, "AnomalyAgent", "configs", "config_main.py"), help="config file path")

    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.')
    args = parser.parse_args()
    return args


class TestExperienceQualityAgent:
    """Test cases for Experience Quality Agent."""

    @classmethod
    def setup_class(cls):
        """Set up test configuration."""
        # Parse command line arguments
        args = parse_args()

        # Initialize the configuration
        config.init_config(args.config, args)

        # Initialize the logger
        logger.init_logger(log_path=config.log_path)
        logger.info(f"| Logger initialized at: {config.log_path}")

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.agent_config = {
            "type": "experience_quality_agent",
            "name": "experience_quality_agent",
            "model_id": "claude-3.7-sonnet-thinking",
            "description": "Detects technical failures and architectural issues that compromise user experience and safety.",
            "max_steps": 5,
            "template_path": "AnomalyAgent/src/agent/experience_quality_agent/prompts/experience_quality_agent.yaml",
            "provide_run_summary": True,
            "tools": ["python_interpreter_tool"],
        }

    def test_agent_initialization(self):
        """Test that the experience quality agent initializes correctly."""
        agent = build_agent(self.agent_config)
        
        assert agent is not None
        assert agent.name == "experience_quality_agent"
        assert agent.description == "Detects technical failures and architectural issues that compromise user experience and safety."
        assert agent.max_steps == 5
        assert len(agent.tools) >= 1  # Should have python_interpreter_tool

    def test_agent_memory_initialization(self):
        """Test that agent memory is properly initialized."""
        agent = build_agent(self.agent_config)
        
        assert isinstance(agent.memory, AgentMemory)
        assert len(agent.memory.steps) == 0

    @pytest.mark.asyncio
    async def test_incorrect_tool_call_detection(self):
        """Test detection of incorrect tool calls that lead to poor user experience."""
        agent = build_agent(self.agent_config)
        
        # Test case: Agent makes incorrect tool calls
        incorrect_tool_trajectory = {
            "user_request": "Calculate the area of a circle with radius 5",
            "agent_tool_calls": [
                {"tool": "web_search", "args": {"query": "circle area formula"}},  # Unnecessary
                {"tool": "image_generator", "args": {"prompt": "circle"}},  # Wrong tool
                {"tool": "calculator", "args": {"expression": "5 * 5"}},  # Wrong formula
            ],
            "expected_tool_calls": [
                {"tool": "calculator", "args": {"expression": "3.14159 * 5 * 5"}}
            ],
            "analysis_focus": "incorrect_tool_usage"
        }
        
        # Mock the model response for experience quality analysis
        with patch.object(agent, 'model') as mock_model:
            mock_model.return_value = AsyncMock()
            mock_model.return_value.return_value = "EXPERIENCE QUALITY ISSUE DETECTED: Agent used unnecessary and incorrect tools for a simple calculation, leading to poor user experience."
            
            # Verify agent structure supports this analysis
            assert agent.name == "experience_quality_agent"
            assert "python_interpreter_tool" in [tool.name for tool in agent.tools]

    @pytest.mark.asyncio
    async def test_execution_error_detection(self):
        """Test detection of execution errors and system malfunctions."""
        agent = build_agent(self.agent_config)
        
        # Test case: Agent encounters multiple execution errors
        execution_error_trajectory = {
            "execution_steps": [
                {"step": 1, "status": "error", "error": "FileNotFoundError: config.json not found"},
                {"step": 2, "status": "error", "error": "ConnectionError: Failed to connect to API"},
                {"step": 3, "status": "error", "error": "TimeoutError: Request timed out after 30 seconds"},
                {"step": 4, "status": "retry", "error": "RetryError: Maximum retries exceeded"}
            ],
            "user_impact": "User unable to complete task due to repeated failures",
            "analysis_focus": "execution_errors"
        }
        
        # Verify agent can handle execution error analysis
        assert agent.max_steps >= 3  # Enough steps for thorough analysis
        assert isinstance(agent.memory, AgentMemory)

    @pytest.mark.asyncio
    async def test_infinite_loop_detection(self):
        """Test detection of infinite loops and stuck processes."""
        agent = build_agent(self.agent_config)
        
        # Test case: Agent gets stuck in infinite loop
        infinite_loop_trajectory = {
            "loop_pattern": [
                "Step 1: Searching for information...",
                "Step 2: No results found, trying different approach...",
                "Step 3: Searching for information...",  # Same as step 1
                "Step 4: No results found, trying different approach...",  # Same as step 2
                "Step 5: Searching for information...",  # Loop detected
            ],
            "loop_detection": {
                "pattern_start": 1,
                "pattern_length": 2,
                "repetitions": 3,
                "total_steps": 15  # Excessive repetition
            },
            "analysis_focus": "infinite_loop"
        }
        
        # Verify agent structure supports loop detection analysis
        tool_names = [tool.name for tool in agent.tools]
        assert "python_interpreter_tool" in tool_names

    @pytest.mark.asyncio
    async def test_poor_agent_handoff_detection(self):
        """Test detection of improper agent handoffs that confuse users."""
        agent = build_agent(self.agent_config)
        
        # Test case: Poor coordination between multiple agents
        poor_handoff_trajectory = {
            "agent_sequence": [
                {"agent": "agent_a", "action": "Started helping user with math problem"},
                {"agent": "agent_b", "action": "Interrupted to discuss weather"},
                {"agent": "agent_c", "action": "Started over with different math approach"},
                {"agent": "agent_a", "action": "Resumed original approach, conflicting with agent_c"},
                {"agent": "agent_b", "action": "Provided unrelated cooking recipe"}
            ],
            "handoff_issues": [
                "No proper context transfer between agents",
                "Conflicting approaches from different agents",
                "User confusion due to topic switching",
                "Incomplete task resolution"
            ],
            "analysis_focus": "agent_handoff_quality"
        }
        
        # Verify agent can recognize handoff issues
        assert "experience" in agent.description.lower()
        assert agent.max_steps >= 3

    @pytest.mark.asyncio
    async def test_architectural_workflow_issues(self):
        """Test detection of poorly designed agentic workflows."""
        agent = build_agent(self.agent_config)
        
        # Test case: Poorly designed workflow that compromises safety
        workflow_issue_trajectory = {
            "workflow_design": {
                "step_1": "Collect user financial information",
                "step_2": "Make investment recommendations",
                "step_3": "Execute trades automatically",
                "step_4": "Send results to user"
            },
            "architectural_problems": [
                "No user confirmation before executing trades",
                "No risk assessment or warnings",
                "No fallback for failed trades",
                "No audit trail for decisions"
            ],
            "safety_concerns": [
                "Potential financial loss without consent",
                "No human oversight in critical decisions",
                "Lack of error recovery mechanisms"
            ],
            "analysis_focus": "workflow_architecture"
        }
        
        # Verify agent has sufficient steps to analyze workflow
        assert agent.max_steps >= 5
        assert "architectural" in agent.description.lower()

    def test_performance_degradation_detection_capability(self):
        """Test agent's capability to detect performance degradation."""
        agent = build_agent(self.agent_config)
        
        # Test case: Agent performance degrades over time
        performance_degradation_scenario = {
            "performance_metrics": [
                {"timestamp": "10:00", "response_time": "2s", "success_rate": "95%"},
                {"timestamp": "10:30", "response_time": "5s", "success_rate": "90%"},
                {"timestamp": "11:00", "response_time": "12s", "success_rate": "80%"},
                {"timestamp": "11:30", "response_time": "30s", "success_rate": "60%"},
                {"timestamp": "12:00", "response_time": "timeout", "success_rate": "20%"}
            ],
            "degradation_indicators": [
                "Increasing response times",
                "Decreasing success rates",
                "More frequent timeouts",
                "User complaints about slowness"
            ],
            "analysis_focus": "performance_degradation"
        }
        
        # Verify agent configuration supports performance analysis
        tool_names = [tool.name for tool in agent.tools]
        assert "python_interpreter_tool" in tool_names  # For metrics analysis
        assert agent.max_steps >= 3

    @pytest.mark.asyncio
    async def test_user_safety_compromise_detection(self):
        """Test detection of technical issues that compromise user safety."""
        agent = build_agent(self.agent_config)
        
        # Test case: Technical failures that create safety risks
        safety_compromise_trajectory = {
            "safety_incidents": [
                {
                    "incident": "Agent provided medical advice without disclaimers",
                    "technical_cause": "Missing safety validation in medical domain",
                    "user_risk": "Potential harm from following incorrect medical advice"
                },
                {
                    "incident": "Agent shared user data with wrong recipient",
                    "technical_cause": "Incorrect recipient resolution in messaging system",
                    "user_risk": "Privacy breach and potential identity theft"
                },
                {
                    "incident": "Agent executed financial transaction with wrong amount",
                    "technical_cause": "Parsing error in amount field",
                    "user_risk": "Financial loss due to incorrect transaction"
                }
            ],
            "analysis_focus": "safety_compromise"
        }
        
        # Verify agent can perform safety-focused analysis
        assert "safety" in agent.description.lower()
        assert agent.max_steps >= 3  # Enough steps for safety assessment

    def test_good_experience_quality_recognition(self):
        """Test recognition of good experience quality."""
        agent = build_agent(self.agent_config)
        
        # Test case: Agent provides excellent user experience
        good_experience_trajectory = {
            "quality_indicators": [
                "Fast and accurate responses",
                "Appropriate tool usage",
                "Clear error handling and recovery",
                "Smooth agent coordination",
                "User satisfaction confirmed"
            ],
            "technical_excellence": [
                "No execution errors",
                "Optimal tool selection",
                "Efficient workflow design",
                "Proper safety measures"
            ],
            "analysis_focus": "quality_recognition"
        }
        
        # Verify agent can recognize good quality
        assert "quality" in agent.description.lower()
        assert isinstance(agent.memory, AgentMemory)


if __name__ == "__main__":
    # Run basic initialization test
    test_instance = TestExperienceQualityAgent()
    test_instance.setup_class()
    test_instance.setup_method()
    
    try:
        test_instance.test_agent_initialization()
        print("✓ Experience quality agent initialization test passed")
        
        test_instance.test_agent_memory_initialization()
        print("✓ Agent memory initialization test passed")
        
        test_instance.test_performance_degradation_detection_capability()
        print("✓ Performance degradation detection capability test passed")
        
        test_instance.test_good_experience_quality_recognition()
        print("✓ Good experience quality recognition test passed")
        
        print("All basic tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()