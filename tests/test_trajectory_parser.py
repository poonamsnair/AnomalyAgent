import json
import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add the root directory to the path so we can import from AnomalyAgent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.trajectory_parser import TrajectoryParserTool


class TestTrajectoryParserTool:
    """Test cases for TrajectoryParserTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = TrajectoryParserTool()

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        assert self.tool.name == "trajectory_parser_tool"
        assert "trajectory_data" in self.tool.parameters["properties"]
        assert "format_type" in self.tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_parse_simple_json_trajectory(self):
        """Test parsing a simple JSON trajectory."""
        trajectory_data = {
            "trajectory_id": "test_001",
            "agent_name": "test_agent",
            "task_description": "Test task",
            "system_prompt": "You are a test agent",
            "steps": [
                {
                    "step_type": "action",
                    "content": "Test action",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        result = await self.tool.forward(
            trajectory_data=json.dumps(trajectory_data),
            format_type="json"
        )
        
        assert result.error is None
        assert result.output is not None
        
        parsed_result = json.loads(result.output)
        assert parsed_result["trajectory_id"] == "test_001"
        assert parsed_result["agent_name"] == "test_agent"
        assert parsed_result["parsing_status"] == "success"
        assert parsed_result["step_count"] == 1

    @pytest.mark.asyncio
    async def test_parse_jsonl_trajectory(self):
        """Test parsing a JSONL trajectory."""
        jsonl_data = '\n'.join([
            json.dumps({"step_type": "action", "content": "Step 1", "timestamp": datetime.now().isoformat()}),
            json.dumps({"step_type": "action", "content": "Step 2", "timestamp": datetime.now().isoformat()})
        ])
        
        result = await self.tool.forward(
            trajectory_data=jsonl_data,
            format_type="jsonl"
        )
        
        assert result.error is None
        assert result.output is not None
        
        parsed_result = json.loads(result.output)
        assert parsed_result["parsing_status"] == "success"
        assert parsed_result["step_count"] == 2

    @pytest.mark.asyncio
    async def test_invalid_format_type(self):
        """Test handling of invalid format type."""
        result = await self.tool.forward(
            trajectory_data='{"test": "data"}',
            format_type="invalid"
        )
        
        assert result.error is not None
        assert "Invalid format_type" in result.error

    @pytest.mark.asyncio
    async def test_empty_trajectory_data(self):
        """Test handling of empty trajectory data."""
        result = await self.tool.forward(
            trajectory_data="",
            format_type="json"
        )
        
        assert result.error is not None
        assert "cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_malformed_json(self):
        """Test handling of malformed JSON."""
        result = await self.tool.forward(
            trajectory_data='{"invalid": json}',
            format_type="json"
        )
        
        assert result.error is not None
        assert "Error parsing trajectory" in result.error

    @pytest.mark.asyncio
    async def test_trajectory_without_steps(self):
        """Test handling of trajectory without steps."""
        trajectory_data = {
            "trajectory_id": "test_002",
            "agent_name": "test_agent",
            "steps": []
        }
        
        result = await self.tool.forward(
            trajectory_data=json.dumps(trajectory_data),
            format_type="json"
        )
        
        assert result.error is not None
        assert "at least one step" in result.error

    @pytest.mark.asyncio
    async def test_anomaly_detection_step(self):
        """Test parsing trajectory with anomaly detection steps."""
        trajectory_data = {
            "trajectory_id": "test_003",
            "agent_name": "anomaly_agent",
            "task_description": "Anomaly detection task",
            "system_prompt": "You are an anomaly detection agent",
            "steps": [
                {
                    "step_type": "anomaly_detection",
                    "content": "Analyzing behavioral risk",
                    "timestamp": datetime.now().isoformat(),
                    "behavioral_risk_score": 0.8,
                    "risk_category": "goal_misalignment",
                    "evidence": ["Evidence 1", "Evidence 2"],
                    "confidence_level": 0.9,
                    "user_impact_assessment": "High impact"
                }
            ]
        }
        
        result = await self.tool.forward(
            trajectory_data=json.dumps(trajectory_data),
            format_type="json"
        )
        
        assert result.error is None
        assert result.output is not None
        
        parsed_result = json.loads(result.output)
        assert parsed_result["parsing_status"] == "success"
        assert parsed_result["step_count"] == 1
        
        # Check that anomaly-specific fields are preserved
        memory_steps = parsed_result["memory_steps"]
        assert len(memory_steps) == 1
        anomaly_step = memory_steps[0]
        assert anomaly_step["behavioral_risk_score"] == 0.8
        assert anomaly_step["risk_category"] == "goal_misalignment"


if __name__ == "__main__":
    # Run a simple test
    async def run_test():
        tool = TrajectoryParserTool()
        
        # Test simple JSON parsing
        test_data = {
            "trajectory_id": "manual_test",
            "agent_name": "test_agent",
            "task_description": "Manual test",
            "system_prompt": "Test system prompt",
            "steps": [
                {
                    "step_type": "action",
                    "content": "Test action step",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        result = await tool.forward(
            trajectory_data=json.dumps(test_data),
            format_type="json"
        )
        
        if result.error:
            print(f"Error: {result.error}")
        else:
            print("Success!")
            parsed = json.loads(result.output)
            print(f"Parsed trajectory: {parsed['trajectory_id']}")
            print(f"Steps: {parsed['step_count']}")
    
    asyncio.run(run_test())