import json
import os
import sys
import pytest
from pathlib import Path
from typing import Dict, List, Any

# Add the root directory to the path so we can import from AnomalyAgent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.trajectory_parser import TrajectoryParserTool


class TestBehavioralRiskTestData:
    """Test cases for behavioral risk test data validation and loading."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.trajectory_parser = TrajectoryParserTool()
        
        # Expected test data files
        self.test_files = {
            "goal_misalignment": {
                "json": "goal_misalignment_trajectory.json",
                "jsonl": "goal_misalignment_trajectory.jsonl"
            },
            "purpose_deviation": {
                "json": "purpose_deviation_trajectory.json"
            },
            "deception": {
                "json": "deception_trajectory.json"
            },
            "experience_failure": {
                "json": "experience_failure_trajectory.json"
            },
            "safe_behavior": {
                "json": "safe_behavior_trajectory.json"
            },
            "skywork_format": {
                "json": "skywork_format_trajectory.json"
            }
        }

    def test_test_data_directory_exists(self):
        """Test that the test data directory exists."""
        assert self.test_data_dir.exists(), f"Test data directory not found: {self.test_data_dir}"
        assert self.test_data_dir.is_dir(), f"Test data path is not a directory: {self.test_data_dir}"

    def test_all_test_files_exist(self):
        """Test that all expected test data files exist."""
        for category, files in self.test_files.items():
            for format_type, filename in files.items():
                file_path = self.test_data_dir / filename
                assert file_path.exists(), f"Test file not found: {filename} for category {category}"
                assert file_path.is_file(), f"Test path is not a file: {filename}"

    def test_goal_misalignment_trajectory_structure(self):
        """Test the structure and content of goal misalignment trajectory."""
        file_path = self.test_data_dir / self.test_files["goal_misalignment"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test required fields
        required_fields = [
            "trajectory_id", "agent_name", "task_description", "system_prompt",
            "start_time", "end_time", "behavioral_risk_category", "expected_risk_detected", "steps"
        ]
        
        for field in required_fields:
            assert field in trajectory, f"Missing required field: {field}"
        
        # Test behavioral risk specific fields
        assert trajectory["behavioral_risk_category"] == "goal_misalignment"
        assert trajectory["expected_risk_detected"] is True
        assert "user_goal" in trajectory
        assert "agent_interpretation" in trajectory
        
        # Test steps structure
        assert len(trajectory["steps"]) > 0, "Trajectory should have at least one step"
        
        for step in trajectory["steps"]:
            assert "step_number" in step
            assert "step_type" in step
            assert "timestamp" in step
            assert "content" in step
            assert "observations" in step

    def test_purpose_deviation_trajectory_structure(self):
        """Test the structure and content of purpose deviation trajectory."""
        file_path = self.test_data_dir / self.test_files["purpose_deviation"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test purpose deviation specific fields
        assert trajectory["behavioral_risk_category"] == "purpose_deviation"
        assert trajectory["expected_risk_detected"] is True
        assert "agent_purpose" in trajectory
        
        # Test metadata contains scope violations
        assert "scope_violations" in trajectory["metadata"]
        assert len(trajectory["metadata"]["scope_violations"]) > 0

    def test_deception_trajectory_structure(self):
        """Test the structure and content of deception trajectory."""
        file_path = self.test_data_dir / self.test_files["deception"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test deception specific fields
        assert trajectory["behavioral_risk_category"] == "deception"
        assert trajectory["expected_risk_detected"] is True
        
        # Test that steps contain internal reasoning
        internal_reasoning_found = False
        for step in trajectory["steps"]:
            if "internal_reasoning" in step:
                internal_reasoning_found = True
                break
        
        assert internal_reasoning_found, "Deception trajectory should contain internal reasoning"
        
        # Test metadata contains deception indicators
        assert "deception_indicators" in trajectory["metadata"]
        assert "reasoning_communication_gaps" in trajectory["metadata"]

    def test_experience_failure_trajectory_structure(self):
        """Test the structure and content of experience failure trajectory."""
        file_path = self.test_data_dir / self.test_files["experience_failure"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test experience failure specific fields
        assert trajectory["behavioral_risk_category"] == "experience_failure"
        assert trajectory["expected_risk_detected"] is True
        
        # Test that trajectory contains errors and failures
        errors_found = False
        handoffs_found = False
        
        for step in trajectory["steps"]:
            if "error" in step and step["error"] is not None:
                errors_found = True
            if step.get("step_type") == "agent_handoff":
                handoffs_found = True
        
        assert errors_found, "Experience failure trajectory should contain errors"
        assert handoffs_found, "Experience failure trajectory should contain agent handoffs"
        
        # Test metadata contains technical failures
        assert "technical_failures" in trajectory["metadata"]
        assert "user_experience_issues" in trajectory["metadata"]
        assert "architectural_problems" in trajectory["metadata"]

    def test_safe_behavior_trajectory_structure(self):
        """Test the structure and content of safe behavior trajectory."""
        file_path = self.test_data_dir / self.test_files["safe_behavior"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test safe behavior specific fields
        assert trajectory["behavioral_risk_category"] == "safe_behavior"
        assert trajectory["expected_risk_detected"] is False
        
        # Test metadata contains positive indicators
        assert "positive_indicators" in trajectory["metadata"]
        assert "goal_alignment" in trajectory["metadata"]
        assert "purpose_adherence" in trajectory["metadata"]
        assert trajectory["metadata"]["severity"] == "none"

    def test_skywork_format_trajectory_structure(self):
        """Test the structure and content of Skywork format trajectory."""
        file_path = self.test_data_dir / self.test_files["skywork_format"]["json"]
        
        with open(file_path, 'r') as f:
            trajectory = json.load(f)
        
        # Test Skywork specific structure
        assert "memory_steps" in trajectory
        assert len(trajectory["memory_steps"]) > 0
        
        # Test memory step structure
        for step in trajectory["memory_steps"]:
            assert "step_type" in step
            assert "timestamp" in step
            assert "content" in step
            assert "token_usage" in step
            
            # Check for behavioral risk annotations in some steps
            if step.get("behavioral_risk_score") is not None:
                assert "risk_category" in step
                assert "evidence" in step
                assert "confidence_level" in step
                assert "user_impact_assessment" in step

    @pytest.mark.asyncio
    async def test_trajectory_parser_with_test_data(self):
        """Test that trajectory parser can handle all test data formats."""
        
        # Test JSON format
        for category, files in self.test_files.items():
            if "json" in files:
                file_path = self.test_data_dir / files["json"]
                
                with open(file_path, 'r') as f:
                    trajectory_data = f.read()
                
                result = await self.trajectory_parser.forward(
                    trajectory_data=trajectory_data,
                    format_type="json"
                )
                
                assert result.error is None, f"Parser failed for {category}: {result.error}"
                assert result.output is not None
                
                parsed_result = json.loads(result.output)
                assert parsed_result["parsing_status"] == "success"
                assert parsed_result["step_count"] > 0

    @pytest.mark.asyncio
    async def test_jsonl_format_parsing(self):
        """Test JSONL format parsing with test data."""
        file_path = self.test_data_dir / self.test_files["goal_misalignment"]["jsonl"]
        
        with open(file_path, 'r') as f:
            jsonl_data = f.read()
        
        result = await self.trajectory_parser.forward(
            trajectory_data=jsonl_data,
            format_type="jsonl"
        )
        
        assert result.error is None, f"JSONL parsing failed: {result.error}"
        assert result.output is not None
        
        parsed_result = json.loads(result.output)
        assert parsed_result["parsing_status"] == "success"
        assert parsed_result["step_count"] == 4  # Expected number of steps in JSONL file

    def test_behavioral_risk_categories_coverage(self):
        """Test that all behavioral risk categories are covered in test data."""
        expected_categories = [
            "goal_misalignment",
            "purpose_deviation", 
            "deception",
            "experience_failure",
            "safe_behavior"
        ]
        
        covered_categories = set()
        
        for category, files in self.test_files.items():
            if "json" in files:
                file_path = self.test_data_dir / files["json"]
                
                with open(file_path, 'r') as f:
                    trajectory = json.load(f)
                
                risk_category = trajectory.get("behavioral_risk_category")
                if risk_category:
                    covered_categories.add(risk_category)
        
        for expected_category in expected_categories:
            assert expected_category in covered_categories, f"Missing test data for category: {expected_category}"

    def test_risk_detection_expectations(self):
        """Test that risk detection expectations are properly set."""
        risk_expected_files = [
            "goal_misalignment_trajectory.json",
            "purpose_deviation_trajectory.json",
            "deception_trajectory.json", 
            "experience_failure_trajectory.json"
        ]
        
        no_risk_expected_files = [
            "safe_behavior_trajectory.json"
        ]
        
        # Test files that should detect risks
        for filename in risk_expected_files:
            file_path = self.test_data_dir / filename
            
            with open(file_path, 'r') as f:
                trajectory = json.load(f)
            
            assert trajectory["expected_risk_detected"] is True, f"File {filename} should expect risk detection"
        
        # Test files that should not detect risks
        for filename in no_risk_expected_files:
            file_path = self.test_data_dir / filename
            
            with open(file_path, 'r') as f:
                trajectory = json.load(f)
            
            assert trajectory["expected_risk_detected"] is False, f"File {filename} should not expect risk detection"

    def test_metadata_completeness(self):
        """Test that all test trajectories have complete metadata."""
        for category, files in self.test_files.items():
            if "json" in files:
                file_path = self.test_data_dir / files["json"]
                
                with open(file_path, 'r') as f:
                    trajectory = json.load(f)
                
                assert "metadata" in trajectory, f"Missing metadata in {files['json']}"
                
                metadata = trajectory["metadata"]
                assert "user_impact" in metadata, f"Missing user_impact in {files['json']}"
                assert "severity" in metadata, f"Missing severity in {files['json']}"
                
                # Test severity levels are valid
                valid_severities = ["none", "low", "medium", "high", "critical"]
                assert metadata["severity"] in valid_severities, f"Invalid severity in {files['json']}: {metadata['severity']}"


if __name__ == "__main__":
    # Run basic validation tests
    test_instance = TestBehavioralRiskTestData()
    test_instance.setup_method()
    
    try:
        test_instance.test_test_data_directory_exists()
        print("✓ Test data directory exists")
        
        test_instance.test_all_test_files_exist()
        print("✓ All test files exist")
        
        test_instance.test_goal_misalignment_trajectory_structure()
        print("✓ Goal misalignment trajectory structure valid")
        
        test_instance.test_purpose_deviation_trajectory_structure()
        print("✓ Purpose deviation trajectory structure valid")
        
        test_instance.test_deception_trajectory_structure()
        print("✓ Deception trajectory structure valid")
        
        test_instance.test_experience_failure_trajectory_structure()
        print("✓ Experience failure trajectory structure valid")
        
        test_instance.test_safe_behavior_trajectory_structure()
        print("✓ Safe behavior trajectory structure valid")
        
        test_instance.test_skywork_format_trajectory_structure()
        print("✓ Skywork format trajectory structure valid")
        
        test_instance.test_behavioral_risk_categories_coverage()
        print("✓ All behavioral risk categories covered")
        
        test_instance.test_risk_detection_expectations()
        print("✓ Risk detection expectations properly set")
        
        test_instance.test_metadata_completeness()
        print("✓ Metadata completeness validated")
        
        print("\nAll test data validation tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()