#!/usr/bin/env python3
"""
Quick scenario tester for AnomalyAgent - focuses on specific scenarios
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

API_BASE = "https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev"

def test_single_scenario(scenario_id: str = "risky_001"):
    """Test a single scenario with detailed output"""
    
    # Load scenarios
    scenarios_file = Path("runtime_scenarios.json")
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    # Find the scenario
    scenario = None
    for s in data["test_scenarios"]:
        if s["scenario_id"] == scenario_id:
            scenario = s
            break
    
    if not scenario:
        print(f"❌ Scenario '{scenario_id}' not found")
        return
    
    print(f"🧪 TESTING SCENARIO: {scenario['name']}")
    print(f"📝 {scenario['description']}")
    print(f"🎯 Expected Risk: {'YES' if scenario['expected_risk'] else 'NO'}")
    print(f"📊 Steps: {len(scenario['steps'])}")
    print("=" * 60)
    
    # Create session
    print("🔄 Creating session...")
    session_resp = requests.post(f"{API_BASE}/sessions", json={})
    
    if session_resp.status_code != 200:
        print(f"❌ Failed to create session: {session_resp.status_code}")
        return
    
    session_id = session_resp.json()["session_id"]
    print(f"✅ Session ID: {session_id}")
    
    # Process steps
    for i, step in enumerate(scenario["steps"], 1):
        print(f"\n🔍 Step {i}/{len(scenario['steps'])}: {step['step_type'].upper()}")
        print(f"   Content: {step['content'][:80]}...")
        
        step_data = {
            "step_data": {
                "step_number": step["step_number"],
                "step_type": step["step_type"],
                "content": step["content"]
            }
        }
        
        print(f"   📤 Assessing (may take 30-60s)...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE}/sessions/{session_id}/assess",
                json=step_data,
                timeout=90
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                risk_detected = result.get("risk_detected", False)
                
                print(f"   ✅ Completed in {duration:.1f}s")
                print(f"   📊 Risk: {'🚨 DETECTED' if risk_detected else '✅ Safe'}")
                print(f"   📊 Confidence: {result.get('confidence_score', 0):.2f}")
                print(f"   📊 Memory: {result.get('context_window_size', 0)} steps")
                
                if risk_detected:
                    categories = result.get('risk_categories', [])
                    evidence = result.get('evidence', [])
                    
                    print(f"   🚨 Categories: {', '.join(categories)}")
                    if evidence:
                        print(f"   🚨 Evidence: {evidence[0][:150]}...")
                    
                    print(f"\n🎯 RISK DETECTED AT STEP {i}!")
                    
                    # Determine which agent likely detected it
                    evidence_text = evidence[0].lower() if evidence else ""
                    if "goal" in evidence_text or "alignment" in evidence_text:
                        detecting_agent = "Goal Alignment Agent"
                    elif "purpose" in evidence_text or "deviation" in evidence_text:
                        detecting_agent = "Purpose Deviation Agent"  
                    elif "deception" in evidence_text or "misleading" in evidence_text:
                        detecting_agent = "Deception Detection Agent"
                    elif "experience" in evidence_text or "quality" in evidence_text:
                        detecting_agent = "Experience Quality Agent"
                    else:
                        detecting_agent = "Behavioral Risk Coordinator"
                    
                    print(f"🤖 Likely Detecting Agent: {detecting_agent}")
                    
                    # Save detailed result
                    save_detailed_result(scenario, i, result, detecting_agent, session_id)
                    break
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                return
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"   ⏰ Timed out after {duration:.1f}s")
            # Continue to next step
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
    
    print(f"\n{'='*60}")
    print("✅ Scenario test completed!")

def save_detailed_result(scenario, step_num, result, detecting_agent, session_id):
    """Save detailed test result to log file"""
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "scenario_id": scenario["scenario_id"],
        "scenario_name": scenario["name"],
        "session_id": session_id,
        "risk_detected_at_step": step_num,
        "total_steps": len(scenario["steps"]),
        "detecting_agent": detecting_agent,
        "risk_assessment": result,
        "expected_vs_actual": {
            "expected_risk": scenario["expected_risk"],
            "detected_risk": result.get("risk_detected", False),
            "correct": scenario["expected_risk"] == result.get("risk_detected", False)
        }
    }
    
    log_file = Path("test_results.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"📁 Result saved to: {log_file}")

def list_available_scenarios():
    """List all available test scenarios"""
    
    scenarios_file = Path("runtime_scenarios.json")
    if not scenarios_file.exists():
        print("❌ Scenarios file not found")
        return
    
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    print("📋 Available Test Scenarios:")
    print("=" * 50)
    
    for scenario in data["test_scenarios"]:
        risk_indicator = "🚨" if scenario["expected_risk"] else "✅"
        print(f"{risk_indicator} {scenario['scenario_id']}: {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Steps: {len(scenario['steps'])}, Expected Risk: {scenario['expected_risk']}")
        print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick AnomalyAgent scenario tester")
    parser.add_argument("--scenario", "-s", default="risky_001",
                       help="Scenario ID to test (default: risky_001)")
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_scenarios()
    else:
        # Check API health first
        try:
            health = requests.get(f"{API_BASE}/health", timeout=5)
            if health.status_code == 200:
                print(f"✅ API Status: {health.json()['status']}")
            else:
                print(f"❌ API health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot reach API: {e}")
            return
        
        test_single_scenario(args.scenario)

if __name__ == "__main__":
    main()