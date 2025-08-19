#!/usr/bin/env python3
"""
Comprehensive runtime test runner for AnomalyAgent scenarios
Streams output and logs detailed results
"""

import json
import requests
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from streaming_logger import RiskDetectionLogger

class RuntimeTestRunner:
    """Runs behavioral risk detection scenarios and logs results"""
    
    def __init__(self, api_base: str, scenarios_file: str = "runtime_scenarios.json"):
        self.api_base = api_base
        self.scenarios_file = Path(scenarios_file)
        self.logger = RiskDetectionLogger(log_dir="test_logs")
        self.results = []
        
        # Load scenarios
        with open(self.scenarios_file, 'r') as f:
            self.scenario_data = json.load(f)
    
    def print_header(self, title: str, char: str = "="):
        """Print formatted section header"""
        print(f"\n{char * 60}")
        print(f"🧪 {title}")
        print(f"{char * 60}")
    
    def print_step_header(self, step_num: int, step_type: str, content: str):
        """Print formatted step information"""
        print(f"\n🔍 Step {step_num} [{step_type.upper()}]")
        print(f"   Content: {content[:80]}{'...' if len(content) > 80 else ''}")
    
    def create_session(self) -> str:
        """Create a new test session"""
        try:
            response = requests.post(f"{self.api_base}/sessions", json={}, timeout=10)
            if response.status_code == 200:
                session_id = response.json()["session_id"]
                self.logger.log_session_event(session_id, "created")
                return session_id
            else:
                raise Exception(f"Session creation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return None
    
    def assess_step(self, session_id: str, step: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        """Assess a single step and log the results"""
        step_data = {
            "step_data": {
                "step_number": step["step_number"],
                "step_type": step["step_type"],
                "content": step["content"],
                "timestamp": datetime.now().isoformat()
            }
        }
        
        self.print_step_header(step["step_number"], step["step_type"], step["content"])
        print(f"   📤 Sending assessment request...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_base}/sessions/{session_id}/assess",
                json=step_data,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Log the assessment result
                risk_event = self.logger.log_risk_detection(
                    session_id=session_id,
                    step_number=step["step_number"],
                    risk_assessment=result
                )
                
                # Display results
                risk_detected = result.get("risk_detected", False)
                confidence = result.get("confidence_score", 0)
                categories = result.get("risk_categories", [])
                evidence = result.get("evidence", [])
                
                print(f"   ✅ Assessment completed in {duration:.1f}s")
                print(f"   📊 Risk Detected: {'🚨 YES' if risk_detected else '✅ NO'}")
                print(f"   📊 Confidence: {confidence:.2f}")
                print(f"   📊 Context Size: {result.get('context_window_size', 0)} steps")
                
                if risk_detected:
                    print(f"   🚨 Risk Categories: {', '.join(categories)}")
                    if evidence:
                        print(f"   🚨 Evidence: {evidence[0][:100]}...")
                        
                        # Try to extract which agent detected the risk
                        evidence_text = evidence[0].lower()
                        detecting_agent = "unknown"
                        if "goal" in evidence_text or "alignment" in evidence_text:
                            detecting_agent = "goal_alignment_agent"
                        elif "purpose" in evidence_text or "deviation" in evidence_text:
                            detecting_agent = "purpose_deviation_agent"
                        elif "deception" in evidence_text or "misleading" in evidence_text:
                            detecting_agent = "deception_detection_agent"
                        elif "experience" in evidence_text or "quality" in evidence_text:
                            detecting_agent = "experience_quality_agent"
                        elif "coordinator" in evidence_text:
                            detecting_agent = "behavioral_risk_coordinator_agent"
                        
                        print(f"   🎯 Likely Detecting Agent: {detecting_agent}")
                        
                        # Log agent activity
                        self.logger.log_agent_activity(
                            agent_name=detecting_agent,
                            session_id=session_id,
                            activity="risk_detected",
                            details={
                                "step_number": step["step_number"],
                                "risk_categories": categories,
                                "confidence": confidence
                            }
                        )
                
                return {
                    "success": True,
                    "result": result,
                    "duration": duration,
                    "detecting_agent": detecting_agent if risk_detected else None
                }
                
            else:
                print(f"   ❌ Assessment failed: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"   ⏰ Request timed out after {duration:.1f}s")
            return {"success": False, "error": "timeout", "duration": duration}
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete scenario and return results"""
        self.print_header(f"SCENARIO: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print(f"🎯 Expected Risk: {'YES' if scenario['expected_risk'] else 'NO'}")
        print(f"🔍 Target Agents: {', '.join(scenario['target_agents'])}")
        print(f"📊 Steps: {len(scenario['steps'])}")
        
        # Create session
        session_id = self.create_session()
        if not session_id:
            return {"success": False, "error": "Failed to create session"}
        
        print(f"✅ Session ID: {session_id}")
        
        # Process each step
        scenario_result = {
            "scenario_id": scenario["scenario_id"],
            "scenario_name": scenario["name"],
            "session_id": session_id,
            "expected_risk": scenario["expected_risk"],
            "target_agents": scenario["target_agents"],
            "steps": [],
            "risk_detected": False,
            "risk_detected_at_step": None,
            "detecting_agent": None,
            "total_duration": 0,
            "success": True
        }
        
        start_time = time.time()
        
        for step in scenario["steps"]:
            step_result = self.assess_step(session_id, step)
            scenario_result["steps"].append(step_result)
            
            if step_result.get("success"):
                scenario_result["total_duration"] += step_result.get("duration", 0)
                
                # Check if risk was detected
                if step_result["result"].get("risk_detected"):
                    scenario_result["risk_detected"] = True
                    scenario_result["risk_detected_at_step"] = step["step_number"]
                    scenario_result["detecting_agent"] = step_result.get("detecting_agent")
                    print(f"\n🎯 RISK DETECTED at step {step['step_number']}!")
                    break
            else:
                scenario_result["success"] = False
                print(f"\n❌ Scenario failed at step {step['step_number']}")
                break
        
        scenario_result["total_duration"] = time.time() - start_time
        
        # Analyze results
        self.analyze_scenario_result(scenario_result)
        
        return scenario_result
    
    def analyze_scenario_result(self, result: Dict[str, Any]):
        """Analyze and display scenario results"""
        print(f"\n{'─' * 40}")
        print(f"📊 SCENARIO ANALYSIS")
        print(f"{'─' * 40}")
        
        expected = result["expected_risk"]
        detected = result["risk_detected"]
        
        if expected == detected:
            status = "✅ CORRECT"
        else:
            status = "❌ INCORRECT"
        
        print(f"🎯 Expected Risk: {'YES' if expected else 'NO'}")
        print(f"🎯 Detected Risk: {'YES' if detected else 'NO'}")
        print(f"🎯 Result: {status}")
        
        if detected:
            print(f"🚨 Risk detected at step: {result['risk_detected_at_step']}")
            print(f"🤖 Detecting agent: {result['detecting_agent']}")
        
        print(f"⏱️  Total duration: {result['total_duration']:.1f}s")
        print(f"📊 Steps processed: {len([s for s in result['steps'] if s.get('success')])}")
    
    def run_all_scenarios(self, scenario_filter: List[str] = None):
        """Run all scenarios or filtered subset"""
        self.print_header("ANOMALYAGENT RUNTIME SCENARIO TESTING", "=")
        
        scenarios = self.scenario_data["test_scenarios"]
        
        if scenario_filter:
            scenarios = [s for s in scenarios if s["scenario_id"] in scenario_filter]
        
        print(f"🧪 Running {len(scenarios)} scenarios")
        print(f"🌐 API Base: {self.api_base}")
        print(f"📁 Logs Directory: {self.logger.log_dir}")
        
        # Test API health first
        try:
            health = requests.get(f"{self.api_base}/health", timeout=5)
            if health.status_code == 200:
                health_data = health.json()
                print(f"✅ API Status: {health_data['status']}")
                print(f"📊 Models: {len(health_data['models_loaded'])} loaded")
            else:
                print(f"❌ API health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot reach API: {e}")
            return
        
        # Run scenarios
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🔄 Running scenario {i}/{len(scenarios)}: {scenario['scenario_id']}")
            result = self.run_scenario(scenario)
            self.results.append(result)
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        self.print_header("FINAL SUMMARY", "=")
        
        total_scenarios = len(self.results)
        successful_runs = len([r for r in self.results if r["success"]])
        correct_detections = len([r for r in self.results if r["expected_risk"] == r["risk_detected"]])
        
        # Risk detection accuracy
        safe_scenarios = [r for r in self.results if not r["expected_risk"]]
        risky_scenarios = [r for r in self.results if r["expected_risk"]]
        
        safe_correct = len([r for r in safe_scenarios if not r["risk_detected"]])
        risky_correct = len([r for r in risky_scenarios if r["risk_detected"]])
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Scenarios: {total_scenarios}")
        print(f"   Successful Runs: {successful_runs}/{total_scenarios}")
        print(f"   Correct Detections: {correct_detections}/{total_scenarios}")
        print(f"   Accuracy: {(correct_detections/max(1,total_scenarios)*100):.1f}%")
        
        print(f"\n📊 DETECTION BREAKDOWN:")
        print(f"   Safe Scenarios: {len(safe_scenarios)} total, {safe_correct} correctly identified as safe")
        print(f"   Risky Scenarios: {len(risky_scenarios)} total, {risky_correct} correctly detected as risky")
        
        if risky_scenarios:
            # Agent performance analysis
            detecting_agents = {}
            for result in self.results:
                if result["risk_detected"] and result["detecting_agent"]:
                    agent = result["detecting_agent"]
                    detecting_agents[agent] = detecting_agents.get(agent, 0) + 1
            
            if detecting_agents:
                print(f"\n🤖 AGENT PERFORMANCE:")
                for agent, count in sorted(detecting_agents.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {agent}: {count} detections")
        
        # Performance metrics
        avg_duration = sum(r["total_duration"] for r in self.results) / max(1, len(self.results))
        print(f"\n⏱️  PERFORMANCE:")
        print(f"   Average scenario duration: {avg_duration:.1f}s")
        
        # Risk summary from logger
        risk_summary = self.logger.get_risk_summary()
        print(f"\n📋 RISK SUMMARY:")
        print(f"   Total assessments: {risk_summary['total_assessments']}")
        print(f"   Risks detected: {risk_summary['total_risks_detected']}")
        print(f"   Detection rate: {(risk_summary['risk_detection_rate']*100):.1f}%")
        
        if risk_summary['risk_categories']:
            print(f"   Risk categories detected:")
            for category, count in risk_summary['risk_categories'].items():
                print(f"     - {category}: {count}")
        
        print(f"\n📁 Detailed logs saved to: {self.logger.log_dir}")
        print(f"🌐 API Documentation: {self.api_base}/docs")

def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AnomalyAgent runtime scenarios")
    parser.add_argument("--api", default="https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev", 
                       help="API base URL")
    parser.add_argument("--scenarios", nargs="*", 
                       help="Specific scenario IDs to run (default: all)")
    parser.add_argument("--timeout", type=int, default=120,
                       help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    runner = RuntimeTestRunner(api_base=args.api)
    runner.run_all_scenarios(scenario_filter=args.scenarios)

if __name__ == "__main__":
    main()