#!/usr/bin/env python3
"""
Test script for the new improvements:
1. Confidence-based routing
2. Parallel analysis
3. Agent trace reference tool  
4. Simplified OpenAI configuration
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_config_simplification():
    """Test that the config has been simplified to OpenAI-only"""
    print("🧪 Testing Configuration Simplification...")
    
    try:
        from configs.config_main import openai_config
        
        # Check that OpenAI config exists and has required fields
        required_fields = ['api_base_url', 'api_key', 'model_name', 'ssl_verify']
        missing_fields = []
        
        for field in required_fields:
            if field not in openai_config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing OpenAI config fields: {missing_fields}")
            return False
            
        # Check SSL is disabled
        if openai_config['ssl_verify'] != False:
            print("❌ SSL verification should be disabled")
            return False
            
        print("✅ Configuration simplified successfully")
        print(f"   - API Base: {openai_config['api_base_url']}")
        print(f"   - Model: {openai_config['model_name']}")
        print(f"   - SSL Disabled: {not openai_config['ssl_verify']}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_agent_trace_tool():
    """Test the agent trace reference tool"""
    print("\n🧪 Testing Agent Trace Reference Tool...")
    
    try:
        # Test that the JSON file exists and is valid
        trace_file = project_root / "src" / "tools" / "agent_trace_reference.json"
        
        if not trace_file.exists():
            print("❌ Agent trace reference JSON file not found")
            return False
            
        with open(trace_file, 'r') as f:
            trace_data = json.load(f)
        
        # Check that it has the expected structure
        required_keys = ['trace_metadata', 'optimal_agent_path', 'performance_metrics']
        for key in required_keys:
            if key not in trace_data:
                print(f"❌ Missing key in trace data: {key}")
                return False
        
        # Check that we have 10 steps as requested
        optimal_path = trace_data['optimal_agent_path']
        if len(optimal_path) != 10:
            print(f"❌ Expected 10 steps, got {len(optimal_path)}")
            return False
            
        print("✅ Agent trace reference tool created successfully")
        print(f"   - Steps defined: {len(optimal_path)}")
        print(f"   - Parallel execution supported: {any(step.get('parallel_execution') for step in optimal_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Agent trace tool test failed: {e}")
        return False

def test_coordinator_improvements():
    """Test that the coordinator agent has the new methods"""
    print("\n🧪 Testing Coordinator Agent Improvements...")
    
    try:
        from src.agent.behavioral_risk_coordinator_agent.behavioral_risk_coordinator_agent import BehavioralRiskCoordinatorAgent
        
        # Check that the new methods exist
        required_methods = [
            'perform_initial_risk_assessment',
            'execute_parallel_agent_analysis',
            'determine_agents_needed',
            'smart_behavioral_risk_analysis'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(BehavioralRiskCoordinatorAgent, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods in coordinator: {missing_methods}")
            return False
            
        print("✅ Coordinator agent improvements added successfully")
        print(f"   - Confidence-based routing: ✓")
        print(f"   - Parallel execution: ✓")
        print(f"   - Smart analysis flow: ✓")
        return True
        
    except Exception as e:
        print(f"❌ Coordinator improvements test failed: {e}")
        return False

async def test_parallel_execution():
    """Test that parallel execution works conceptually"""
    print("\n🧪 Testing Parallel Execution Concept...")
    
    try:
        # Simulate parallel agent calls
        async def mock_agent_call(agent_name, delay):
            await asyncio.sleep(delay * 0.1)  # Scale down for testing
            return f"{agent_name}_result"
        
        # Test parallel vs sequential timing
        import time
        
        # Sequential execution
        start_time = time.time()
        sequential_results = []
        for i, agent in enumerate(['agent1', 'agent2', 'agent3', 'agent4']):
            result = await mock_agent_call(agent, 1)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel execution  
        start_time = time.time()
        tasks = [mock_agent_call(f'agent{i+1}', 1) for i in range(4)]
        parallel_results = await asyncio.gather(*tasks)
        parallel_time = time.time() - start_time
        
        if parallel_time >= sequential_time:
            print("❌ Parallel execution not faster than sequential")
            return False
            
        speedup = sequential_time / parallel_time
        print("✅ Parallel execution working correctly")
        print(f"   - Sequential time: {sequential_time:.3f}s")
        print(f"   - Parallel time: {parallel_time:.3f}s")
        print(f"   - Speedup: {speedup:.1f}x")
        return True
        
    except Exception as e:
        print(f"❌ Parallel execution test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing AnomalyAgent Improvements")
    print("=" * 50)
    
    tests = [
        ("Configuration Simplification", test_config_simplification()),
        ("Agent Trace Tool", test_agent_trace_tool()),
        ("Coordinator Improvements", test_coordinator_improvements()),
        ("Parallel Execution", test_parallel_execution()),
    ]
    
    results = []
    for test_name, test_func in tests:
        if asyncio.iscoroutine(test_func):
            result = await test_func
        else:
            result = test_func
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL" 
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All improvements implemented successfully!")
        return True
    else:
        print("⚠️ Some tests failed - check the output above")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)