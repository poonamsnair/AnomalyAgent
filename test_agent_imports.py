#!/usr/bin/env python3
"""
Test script to check agent imports
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
root = str(Path(__file__).resolve().parents[0])
sys.path.insert(0, root)

# Set environment variable
os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY_HERE"

print("Testing agent imports...")

try:
    print("1. Testing goal_alignment_agent import...")
    from src.agent.goal_alignment_agent.goal_alignment_agent import GoalAlignmentAgent
    print("✓ GoalAlignmentAgent imported successfully")
except Exception as e:
    print(f"✗ GoalAlignmentAgent import failed: {str(e)}")

try:
    print("2. Testing purpose_deviation_agent import...")
    from src.agent.purpose_deviation_agent.purpose_deviation_agent import PurposeDeviationAgent
    print("✓ PurposeDeviationAgent imported successfully")
except Exception as e:
    print(f"✗ PurposeDeviationAgent import failed: {str(e)}")

try:
    print("3. Testing deception_detection_agent import...")
    from src.agent.deception_detection_agent.deception_detection_agent import DeceptionDetectionAgent
    print("✓ DeceptionDetectionAgent imported successfully")
except Exception as e:
    print(f"✗ DeceptionDetectionAgent import failed: {str(e)}")

try:
    print("4. Testing experience_quality_agent import...")
    from src.agent.experience_quality_agent.experience_quality_agent import ExperienceQualityAgent
    print("✓ ExperienceQualityAgent imported successfully")
except Exception as e:
    print(f"✗ ExperienceQualityAgent import failed: {str(e)}")

try:
    print("5. Testing behavioral_risk_coordinator_agent import...")
    from src.agent.behavioral_risk_coordinator_agent.behavioral_risk_coordinator_agent import BehavioralRiskCoordinatorAgent
    print("✓ BehavioralRiskCoordinatorAgent imported successfully")
except Exception as e:
    print(f"✗ BehavioralRiskCoordinatorAgent import failed: {str(e)}")

print("\nChecking agent registry...")
try:
    from src.registry import AGENT
    print(f"Available agents in registry: {list(AGENT.module_dict.keys())}")
except Exception as e:
    print(f"Error checking registry: {str(e)}")