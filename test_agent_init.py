#!/usr/bin/env python3
"""
Test script to debug agent initialization issues
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
root = str(Path(__file__).resolve().parents[0])
sys.path.insert(0, root)

# Set environment variable
os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY_HERE"

print("Testing agent initialization...")

# Import agents to ensure they are registered
try:
    from src.agent.goal_alignment_agent.goal_alignment_agent import GoalAlignmentAgent
    from src.agent.purpose_deviation_agent.purpose_deviation_agent import PurposeDeviationAgent
    from src.agent.deception_detection_agent.deception_detection_agent import DeceptionDetectionAgent
    from src.agent.experience_quality_agent.experience_quality_agent import ExperienceQualityAgent
    from src.agent.behavioral_risk_coordinator_agent.behavioral_risk_coordinator_agent import BehavioralRiskCoordinatorAgent
    print("0. Agent registrations imported successfully")
except ImportError as e:
    print(f"Warning: Failed to import some agents: {e}")

try:
    print("1. Testing logger import...")
    from src.logger import logger
    print("✓ Logger imported successfully")
    
    print("2. Testing config import...")
    from src.config import config
    print("✓ Config imported successfully")
    
    print("3. Testing model_manager import...")
    from src.models import model_manager
    print("✓ Model manager imported successfully")
    
    print("4. Testing agent import...")
    from src.agent import create_agent
    print("✓ Agent create function imported successfully")
    
    print("5. Initialize configuration...")
    from argparse import Namespace
    config_path = os.path.join(root, "configs", "config_main.py")
    default_args = Namespace(cfg_options={})
    config.init_config(config_path, default_args)
    print("✓ Configuration initialized")
    
    print("6. Initialize logger...")
    logger.init_logger(log_path=config.log_path)
    print("✓ Logger initialized")
    
    print("7. Initialize models...")
    model_manager.init_models(use_local_proxy=True)
    print(f"✓ Models initialized. Available models: {list(model_manager.registed_models.keys())}")
    
    print("8. Creating agent...")
    import asyncio
    
    async def test_agent_creation():
        agent = await create_agent(config)
        return agent
    
    agent = asyncio.run(test_agent_creation())
    print("✓ Agent created successfully!")
    print(f"Agent type: {type(agent)}")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()