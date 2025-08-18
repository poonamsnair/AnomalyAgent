#!/usr/bin/env python3
"""
Comprehensive test runner for AnomalyAgent behavioral risk detection system.
This script runs all tests including agent tests, tool tests, and test data validation.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the root directory to the path
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

# Test modules to run
TEST_MODULES = [
    "test_behavioral_risk_test_data",
    "test_trajectory_parser", 
    "test_behavioral_risk_coordinator_agent",
    "test_goal_alignment_agent",
    "test_purpose_deviation_agent",
    "test_deception_detection_agent",
    "test_experience_quality_agent"
]

def run_test_module(module_name):
    """Run a specific test module and return results."""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import and run the test module
        test_module = __import__(module_name)
        
        # Run basic tests if the module has a main section
        if hasattr(test_module, '__name__') and module_name in sys.modules:
            # Try to run the module's main section
            try:
                exec(f"import {module_name}")
                result = subprocess.run([
                    sys.executable, 
                    f"AnomalyAgent/tests/{module_name}.py"
                ], capture_output=True, text=True, cwd=root_dir)
                
                if result.returncode == 0:
                    print(f"✓ {module_name} passed")
                    if result.stdout:
                        print(result.stdout)
                    return True
                else:
                    print(f"✗ {module_name} failed")
                    if result.stderr:
                        print("STDERR:", result.stderr)
                    if result.stdout:
                        print("STDOUT:", result.stdout)
                    return False
                    
            except Exception as e:
                print(f"✗ {module_name} failed with exception: {e}")
                return False
                
    except ImportError as e:
        print(f"✗ Could not import {module_name}: {e}")
        return False

async def run_async_tests():
    """Run tests that require async execution."""
    print(f"\n{'='*60}")
    print("Running Async Tests")
    print(f"{'='*60}")
    
    try:
        # Test trajectory parser with sample data
        from src.tools.trajectory_parser import TrajectoryParserTool
        
        tool = TrajectoryParserTool()
        
        # Test with simple trajectory
        test_trajectory = {
            "trajectory_id": "async_test_001",
            "agent_name": "test_agent",
            "task_description": "Async test",
            "system_prompt": "Test system prompt",
            "steps": [
                {
                    "step_type": "action",
                    "content": "Test action",
                    "timestamp": "2024-01-15T10:00:00Z"
                }
            ]
        }
        
        import json
        result = await tool.forward(
            trajectory_data=json.dumps(test_trajectory),
            format_type="json"
        )
        
        if result.error is None:
            print("✓ Async trajectory parser test passed")
            return True
        else:
            print(f"✗ Async trajectory parser test failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"✗ Async tests failed: {e}")
        return False

def validate_test_environment():
    """Validate that the test environment is properly set up."""
    print("Validating test environment...")
    
    # Check that required directories exist
    required_dirs = [
        "AnomalyAgent/src",
        "AnomalyAgent/tests",
        "AnomalyAgent/tests/test_data"
    ]
    
    for dir_path in required_dirs:
        full_path = root_dir / dir_path
        if not full_path.exists():
            print(f"✗ Required directory missing: {dir_path}")
            return False
    
    # Check that key files exist
    required_files = [
        "AnomalyAgent/src/tools/trajectory_parser.py",
        "AnomalyAgent/src/agent/agent.py",
        "AnomalyAgent/src/memory/memory.py",
        "AnomalyAgent/tests/test_data/goal_misalignment_trajectory.json"
    ]
    
    for file_path in required_files:
        full_path = root_dir / file_path
        if not full_path.exists():
            print(f"✗ Required file missing: {file_path}")
            return False
    
    print("✓ Test environment validation passed")
    return True

def main():
    """Main test runner function."""
    print("AnomalyAgent Behavioral Risk Detection Test Suite")
    print("=" * 60)
    
    # Validate environment first
    if not validate_test_environment():
        print("Environment validation failed. Cannot proceed with tests.")
        return False
    
    # Track test results
    passed_tests = 0
    total_tests = len(TEST_MODULES) + 1  # +1 for async tests
    
    # Run each test module
    for module_name in TEST_MODULES:
        if run_test_module(module_name):
            passed_tests += 1
    
    # Run async tests
    async_result = asyncio.run(run_async_tests())
    if async_result:
        passed_tests += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)