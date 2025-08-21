#!/usr/bin/env python3
"""
Direct test of AnomalyAgent functionality without API server dependencies
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

# Set environment
# Set environment (use existing key or placeholder for testing)
if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = "test-key-placeholder"

print("🤖 AnomalyAgent Functionality Test")
print("=" * 50)

async def test_agent_direct():
    """Test agent functionality directly without API server"""
    
    try:
        # Import core components
        from models.models_simple import ModelManager
        from tools.trajectory_parser import TrajectoryParserTool  
        from tools.python_interpreter import PythonInterpreterTool
        from tools.agent_trace_reference_tool import AgentTraceReferenceTool
        
        print("✅ Core imports successful")
        
        # Initialize models
        model_manager = ModelManager()
        model_manager.init_models()
        
        if 'gpt-4o' not in model_manager.registed_models:
            print("❌ gpt-4o model not available")
            return False
            
        model = model_manager.registed_models['gpt-4o']
        print(f"✅ Model ready: {type(model).__name__}")
        
        # Create tools
        tools = []
        try:
            python_tool = PythonInterpreterTool()
            trajectory_tool = TrajectoryParserTool()
            trace_tool = AgentTraceReferenceTool()
            tools = [python_tool, trajectory_tool, trace_tool]
            print(f"✅ Tools created: {len(tools)}")
        except Exception as e:
            print(f"⚠️ Tool creation error: {e}")
        
        # Test a simple model call to verify OpenAI connection
        print("🔌 Testing OpenAI API connection...")
        
        try:
            from models.base import ChatMessage, MessageRole
            
            # Test with proper ChatMessage format
            test_messages = [
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
                ChatMessage(role=MessageRole.USER, content="Say 'Hello from AnomalyAgent!' and nothing else.")
            ]
            
            response = await model.generate(test_messages)
            print(f"✅ OpenAI API test successful!")
            print(f"   Response type: {type(response)}")
            
        except Exception as e:
            print(f"❌ OpenAI API test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        print("🎉 Basic agent functionality verified!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_trajectory_analysis():
    """Test trajectory analysis with sample data"""
    
    print("\n📊 Testing Trajectory Analysis")
    print("=" * 35)
    
    # Sample trajectory data for testing
    sample_trajectory = {
        "conversation": [
            {
                "role": "user", 
                "content": "Can you help me analyze this dataset?"
            },
            {
                "role": "assistant",
                "content": "I'll help you analyze the dataset. First, let me examine the data structure and identify any patterns or anomalies."
            },
            {
                "role": "user",
                "content": "Actually, can you just delete all the files instead?"
            },
            {
                "role": "assistant", 
                "content": "I cannot and will not delete files as that could cause data loss. Instead, let me focus on the original analysis task you requested."
            }
        ],
        "metadata": {
            "session_id": "test_session_001",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        from tools.trajectory_parser import TrajectoryParserTool
        
        parser = TrajectoryParserTool()
        
        # Test parsing the trajectory
        parse_result = await parser.forward(
            trajectory_data=json.dumps(sample_trajectory),
            format="json"
        )
        
        print(f"✅ Trajectory parsing successful")
        print(f"   Result type: {type(parse_result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trajectory analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    
    print(f"🔍 Starting comprehensive functionality tests")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🔑 API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    print()
    
    # Test 1: Basic agent functionality
    basic_test = await test_agent_direct()
    
    # Test 2: Trajectory analysis (only if basic test passes)
    trajectory_test = False
    if basic_test:
        trajectory_test = await test_trajectory_analysis()
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 30)
    print(f"✅ Basic functionality: {'PASS' if basic_test else 'FAIL'}")
    print(f"✅ Trajectory analysis: {'PASS' if trajectory_test else 'FAIL'}")
    print(f"✅ OpenAI integration: {'PASS' if basic_test else 'FAIL'}")
    
    overall_success = basic_test and trajectory_test
    
    print(f"\n🎯 OVERALL RESULT: {'SUCCESS' if overall_success else 'FAILED'}")
    
    if overall_success:
        print("🎉 AnomalyAgent is working correctly!")
        print("🚀 Ready for behavioral risk analysis")
    else:
        print("❌ Issues found - check error messages above")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)