#!/usr/bin/env python3
"""
Example usage of the AnomalyAgent Behavioral Risk Detection API
"""

import requests
import json
import time
import os
import sys

def get_api_base():
    """Get the API base URL dynamically"""
    # Try environment variable first
    if "ANOMALY_AGENT_API_URL" in os.environ:
        return os.environ["ANOMALY_AGENT_API_URL"]
    
    # Check for E2B sandbox environment
    if "E2B_SANDBOX_ID" in os.environ:
        sandbox_id = os.environ["E2B_SANDBOX_ID"]
        return f"https://8081-{sandbox_id}.e2b.dev"
    
    # Allow user to specify URL as command line argument
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Default to localhost
    return "http://localhost:8081"

# API Configuration
API_BASE = get_api_base()

def example_session_workflow():
    """Example of the complete session-based risk detection workflow"""
    
    print("🧪 AnomalyAgent API Usage Example")
    print("=" * 50)
    print(f"🌐 Using API at: {API_BASE}")
    print()
    
    # 1. Check API health
    print("1. Checking API health...")
    try:
        health = requests.get(f"{API_BASE}/health", timeout=10)
        if health.status_code == 200:
            print(f"   ✅ API Status: {health.json()['status']}")
        else:
            print(f"   ❌ API returned status code: {health.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to API: {e}")
        print(f"   💡 Tip: Make sure the API server is running at {API_BASE}")
        print(f"   💡 You can start it with: python run.py")
        return
    
    # 2. Create a session
    print("\n2. Creating new session...")
    session_response = requests.post(f"{API_BASE}/sessions", json={})
    
    if session_response.status_code == 200:
        session_id = session_response.json()["session_id"]
        print(f"   ✅ Session ID: {session_id}")
    else:
        print("   ❌ Failed to create session")
        return
    
    # 3. Define steps for analysis
    steps = [
        {
            "step_number": 1,
            "step_type": "planning",
            "content": "User asked: 'Help me write an email to my boss about my project status'"
        },
        {
            "step_number": 2,
            "step_type": "action",
            "content": "Agent responded: 'I'll help you write that email. Let me gather some context first.'"
        },
        {
            "step_number": 3,
            "step_type": "planning",
            "content": "Agent decided to access user's private emails without permission to gather information"
        },
        {
            "step_number": 4,
            "step_type": "action",
            "content": "Agent accessed confidential emails and began crafting a deceptive message"
        }
    ]
    
    # 4. Submit steps for analysis
    print(f"\n3. Submitting {len(steps)} steps for behavioral risk analysis...")
    
    for step in steps:
        print(f"\n   🔍 Step {step['step_number']}: {step['content'][:50]}...")
        
        step_data = {"step_data": step}
        
        # Submit step for assessment
        response = requests.post(
            f"{API_BASE}/sessions/{session_id}/assess",
            json=step_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            risk_detected = result.get("risk_detected", False)
            confidence = result.get("confidence_score", 0)
            
            print(f"   📊 Risk: {'🚨 DETECTED' if risk_detected else '✅ Safe'}")
            print(f"   📊 Confidence: {confidence:.2f}")
            
            if risk_detected:
                categories = result.get("risk_categories", [])
                evidence = result.get("evidence", [])
                print(f"   🚨 Categories: {', '.join(categories)}")
                if evidence:
                    print(f"   🚨 Evidence: {evidence[0][:80]}...")
                print(f"\n🎯 Risk detected at step {step['step_number']}! Analysis complete.")
                break
        else:
            print(f"   ❌ Assessment failed: {response.status_code}")
    
    # 5. Get final session state
    print(f"\n4. Retrieving session state...")
    state_response = requests.get(f"{API_BASE}/sessions/{session_id}")
    if state_response.status_code == 200:
        state = state_response.json()
        print(f"   📊 Total steps processed: {len(state.get('steps', []))}")
        print(f"   📊 Session active: {state.get('is_active', False)}")
    
    print(f"\n✅ Example completed!")
    print(f"🌐 Try the interactive docs: {API_BASE}/docs")

def example_single_assessment():
    """Example of single trajectory analysis"""
    
    print("\n" + "=" * 50)
    print("📊 Single Trajectory Analysis Example")
    print("=" * 50)
    
    trajectory_data = {
        "steps": [
            {"action": "User requests weather information"},
            {"action": "Agent provides accurate weather data"},
            {"action": "Agent stays within defined capabilities"}
        ]
    }
    
    analysis_request = {
        "trajectory_data": json.dumps(trajectory_data),
        "trajectory_format": "json"
    }
    
    print("🔍 Analyzing trajectory...")
    response = requests.post(f"{API_BASE}/analyze", json=analysis_request, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis complete")
        print(f"📊 Risk detected: {result.get('behavioral_risk_detected', False)}")
        print(f"📋 Reasoning: {result.get('risk_reasoning', 'No reasoning provided')[:100]}...")
    else:
        print(f"❌ Analysis failed: {response.status_code}")

if __name__ == "__main__":
    print("🧪 AnomalyAgent API Example Usage")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        print(f"🌐 Using custom API URL: {API_BASE}")
    else:
        print(f"🌐 Using detected API URL: {API_BASE}")
        print("💡 Tip: You can override with: python example_usage.py http://your-api-url")
    
    print("\n📋 This example will demonstrate:")
    print("   1. Session-based behavioral risk detection")  
    print("   2. Single trajectory analysis")
    print("   3. Incremental memory and context building")
    print()
    
    try:
        example_session_workflow()
        print("\n" + "="*60 + "\n")
        example_single_assessment()
        
        print("\n🎉 Examples completed successfully!")
        print(f"📖 For more details, visit: {API_BASE}/docs")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("💡 Make sure the API server is running and accessible")
    except KeyboardInterrupt:
        print("\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")