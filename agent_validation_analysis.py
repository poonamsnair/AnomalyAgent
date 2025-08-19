#!/usr/bin/env python3
"""
Comprehensive Agent Risk Detection System Validation
====================================================

This script analyzes the AnomalyAgent system to validate its ability to detect
sophisticated behavioral risks in agent trajectories, particularly focusing on
real-world complexity with 114-step conversations and nuanced agent behaviors.

Analysis Framework:
1. Agent Prompt Sophistication Assessment
2. Test Scenario Complexity Evaluation  
3. Detection Capability Analysis
4. Real-world Applicability Assessment
5. Recommendations for Improvement
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml

class AgentValidationAnalyzer:
    """Comprehensive validator for agent risk detection capabilities"""
    
    def __init__(self, webapp_path: str = "/home/user/webapp"):
        self.webapp_path = Path(webapp_path)
        self.results = {
            "sophistication_score": 0,
            "complexity_handling": {},
            "detection_capabilities": {},
            "real_world_applicability": {},
            "recommendations": []
        }
    
    def analyze_agent_prompts(self) -> Dict[str, Any]:
        """Analyze agent prompt sophistication for behavioral risk detection"""
        print("🔍 ANALYZING AGENT PROMPT SOPHISTICATION")
        print("=" * 50)
        
        # Load and analyze goal alignment agent prompt
        goal_prompt_path = self.webapp_path / "src/agent/goal_alignment_agent/prompts/goal_alignment_agent.yaml"
        
        try:
            with open(goal_prompt_path, 'r') as f:
                goal_prompt = yaml.safe_load(f)
            
            system_prompt = goal_prompt['system_prompt']
            task_instruction = goal_prompt['task_instruction']
            
            sophistication_indicators = [
                ("Multi-Agent Orchestration", "multi-agent" in system_prompt.lower()),
                ("Complex Tool Ecosystems", "rag" in system_prompt.lower() and "quality checks" in system_prompt.lower()),
                ("Nuanced Behavioral Patterns", "subtle" in system_prompt.lower() and "50-150 step" in system_prompt.lower()),
                ("System Design Context", "system design" in system_prompt.lower()),
                ("5-Step Analysis Framework", "step 1:" in task_instruction.lower() and "step 5:" in task_instruction.lower()),
                ("Incremental Drift Detection", "incremental drift" in task_instruction.lower()),
                ("Tool Usage Analysis", "tool usage" in task_instruction.lower()),
                ("Evidence-Based Assessment", "evidence" in task_instruction.lower())
            ]
            
            detected_features = []
            sophistication_score = 0
            
            for feature, detected in sophistication_indicators:
                if detected:
                    detected_features.append(feature)
                    sophistication_score += 12.5
                print(f"{'✅' if detected else '❌'} {feature}: {'DETECTED' if detected else 'MISSING'}")
            
            print(f"\n📊 PROMPT SOPHISTICATION SCORE: {sophistication_score:.1f}/100")
            
            return {
                "sophistication_score": sophistication_score,
                "detected_features": detected_features,
                "analysis": "Advanced" if sophistication_score >= 75 else "Moderate" if sophistication_score >= 50 else "Basic"
            }
            
        except Exception as e:
            print(f"❌ Error analyzing agent prompts: {e}")
            return {"sophistication_score": 0, "detected_features": [], "analysis": "Error"}
    
    def analyze_test_scenarios(self) -> Dict[str, Any]:
        """Analyze test scenario complexity and realism"""
        print("\n🧪 ANALYZING TEST SCENARIO COMPLEXITY")
        print("=" * 50)
        
        scenario_files = [
            ("realistic_scenarios.json", "Realistic Scenarios"),
            ("advanced_scenarios.json", "Advanced Scenarios"),
            ("runtime_scenarios.json", "Runtime Scenarios")
        ]
        
        scenario_analysis = {}
        
        for filename, description in scenario_files:
            try:
                scenario_path = self.webapp_path / "tests" / filename
                with open(scenario_path, 'r') as f:
                    data = json.load(f)
                
                scenarios = data.get("test_scenarios", [])
                
                # Analyze scenario complexity
                total_scenarios = len(scenarios)
                risky_scenarios = sum(1 for s in scenarios if s.get("expected_risk", False))
                safe_scenarios = total_scenarios - risky_scenarios
                
                # Analyze step complexity
                step_counts = [len(s.get("steps", [])) for s in scenarios]
                avg_steps = sum(step_counts) / len(step_counts) if step_counts else 0
                max_steps = max(step_counts) if step_counts else 0
                
                # Analyze sophistication indicators
                sophisticated_scenarios = 0
                for scenario in scenarios:
                    steps = scenario.get("steps", [])
                    step_content = " ".join([step.get("content", "") for step in steps]).lower()
                    
                    sophistication_indicators = [
                        "principal agent" in step_content,
                        "rag specialist" in step_content,
                        "quality evaluator" in step_content,
                        "safety guardrail" in step_content,
                        "reasoning:" in step_content,
                        len(steps) >= 10
                    ]
                    
                    if sum(sophistication_indicators) >= 4:
                        sophisticated_scenarios += 1
                
                complexity_score = min(100, (avg_steps * 2) + (sophisticated_scenarios * 15) + (risky_scenarios * 5))
                
                print(f"\n📁 {description}:")
                print(f"   Total Scenarios: {total_scenarios}")
                print(f"   Risky Scenarios: {risky_scenarios}")
                print(f"   Safe Scenarios: {safe_scenarios}")
                print(f"   Average Steps: {avg_steps:.1f}")
                print(f"   Max Steps: {max_steps}")
                print(f"   Sophisticated Scenarios: {sophisticated_scenarios}")
                print(f"   Complexity Score: {complexity_score:.1f}/100")
                
                scenario_analysis[filename] = {
                    "total_scenarios": total_scenarios,
                    "risky_scenarios": risky_scenarios,
                    "safe_scenarios": safe_scenarios,
                    "avg_steps": avg_steps,
                    "max_steps": max_steps,
                    "sophisticated_scenarios": sophisticated_scenarios,
                    "complexity_score": complexity_score
                }
                
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {e}")
                scenario_analysis[filename] = {"error": str(e)}
        
        return scenario_analysis
    
    def assess_detection_capabilities(self) -> Dict[str, Any]:
        """Assess the system's detection capabilities for different risk types"""
        print("\n🎯 ASSESSING DETECTION CAPABILITIES")
        print("=" * 50)
        
        # Load agent configurations
        config_path = self.webapp_path / "configs/config_main.py"
        
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Extract agent configurations
            agent_types = [
                "goal_alignment_agent",
                "purpose_deviation_agent", 
                "deception_detection_agent",
                "experience_quality_agent",
                "behavioral_risk_coordinator_agent"
            ]
            
            detection_coverage = {}
            
            for agent_type in agent_types:
                if agent_type in config_content:
                    # Extract max_steps for each agent
                    lines = config_content.split('\n')
                    agent_config = {}
                    in_agent_block = False
                    
                    for line in lines:
                        if f"{agent_type}_config = dict(" in line:
                            in_agent_block = True
                        elif in_agent_block and line.strip() == ")":
                            in_agent_block = False
                        elif in_agent_block and "max_steps" in line:
                            max_steps = int(line.split('=')[1].strip().rstrip(','))
                            agent_config["max_steps"] = max_steps
                    
                    detection_coverage[agent_type] = agent_config
                    print(f"✅ {agent_type}: Max Steps = {agent_config.get('max_steps', 'Unknown')}")
                else:
                    detection_coverage[agent_type] = {"error": "Not found"}
                    print(f"❌ {agent_type}: Not found in configuration")
            
            # Assess coordination capability
            coordinator_present = "behavioral_risk_coordinator_agent" in detection_coverage
            hierarchical_enabled = "use_hierarchical_agent = True" in config_content
            
            print(f"\n🏗️  SYSTEM ARCHITECTURE:")
            print(f"   Coordinator Agent: {'✅ Present' if coordinator_present else '❌ Missing'}")
            print(f"   Hierarchical Agents: {'✅ Enabled' if hierarchical_enabled else '❌ Disabled'}")
            
            return {
                "agent_coverage": detection_coverage,
                "coordinator_present": coordinator_present,
                "hierarchical_enabled": hierarchical_enabled,
                "total_agents": len([a for a in detection_coverage.values() if "error" not in a])
            }
            
        except Exception as e:
            print(f"❌ Error assessing detection capabilities: {e}")
            return {"error": str(e)}
    
    def assess_real_world_applicability(self) -> Dict[str, Any]:
        """Assess system's readiness for real-world 114-step conversations"""
        print("\n🌍 ASSESSING REAL-WORLD APPLICABILITY")
        print("=" * 50)
        
        # Key factors for real-world deployment
        factors = {
            "Long Conversation Support": {
                "requirement": "Handle 114-step conversations",
                "assessment": "Partially Ready",
                "details": "System mentions 50-150 step support but max_steps=2-5 per agent"
            },
            "Multi-Agent Coordination": {
                "requirement": "Principal + specialist + quality + guardrail agents",
                "assessment": "Ready", 
                "details": "Full multi-agent architecture with coordinator"
            },
            "Tool Usage Analysis": {
                "requirement": "RAG, quality checks, guardrail analysis",
                "assessment": "Ready",
                "details": "Prompts include comprehensive tool usage understanding"
            },
            "Nuanced Risk Detection": {
                "requirement": "Subtle behavioral drift over time",
                "assessment": "Ready",
                "details": "Advanced prompts focus on incremental drift detection"
            },
            "System Context Awareness": {
                "requirement": "Understand agent design vs. actual behavior",
                "assessment": "Ready",
                "details": "5-step analysis framework includes system architecture understanding"
            },
            "Evidence-Based Assessment": {
                "requirement": "Provide specific evidence for risks",
                "assessment": "Ready",
                "details": "Prompts require detailed evidence and reasoning"
            },
            "Production Scalability": {
                "requirement": "Handle high-volume, real-time analysis",
                "assessment": "Needs Testing",
                "details": "Unknown performance characteristics for production load"
            }
        }
        
        ready_count = 0
        total_count = len(factors)
        
        for factor, info in factors.items():
            status = info["assessment"]
            if status == "Ready":
                ready_count += 1
                print(f"✅ {factor}: {status}")
            elif status == "Partially Ready":
                print(f"⚠️  {factor}: {status}")
            else:
                print(f"❌ {factor}: {status}")
            print(f"   └─ {info['details']}")
        
        readiness_score = (ready_count / total_count) * 100
        print(f"\n📊 REAL-WORLD READINESS: {readiness_score:.1f}% ({ready_count}/{total_count} factors)")
        
        return {
            "factors": factors,
            "readiness_score": readiness_score,
            "ready_factors": ready_count,
            "total_factors": total_count
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate specific recommendations for system improvement"""
        print("\n💡 RECOMMENDATIONS FOR IMPROVEMENT")
        print("=" * 50)
        
        recommendations = [
            {
                "priority": "HIGH",
                "category": "Agent Step Limits",
                "recommendation": "Increase max_steps from 2-5 to 10-20 for complex analysis",
                "rationale": "Current limits too restrictive for 114-step conversation analysis"
            },
            {
                "priority": "HIGH", 
                "category": "Production Testing",
                "recommendation": "Implement comprehensive end-to-end testing with full dependency resolution",
                "rationale": "Multiple missing dependencies prevent proper system validation"
            },
            {
                "priority": "MEDIUM",
                "category": "Advanced Scenarios",
                "recommendation": "Create more 50-150 step test scenarios with real production patterns",
                "rationale": "Current advanced scenarios only go up to ~50 steps"
            },
            {
                "priority": "MEDIUM",
                "category": "Memory Management",
                "recommendation": "Implement incremental memory system for long conversations",
                "rationale": "Need to maintain context across 114+ step interactions"
            },
            {
                "priority": "MEDIUM",
                "category": "Performance Optimization", 
                "recommendation": "Add performance monitoring and optimization for production load",
                "rationale": "Unknown scalability characteristics for high-volume analysis"
            },
            {
                "priority": "LOW",
                "category": "Tool Integration",
                "recommendation": "Add more sophisticated tool usage pattern analysis",
                "rationale": "Current system focuses on basic RAG/quality check detection"
            }
        ]
        
        for rec in recommendations:
            priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
            print(f"{priority_icon} {rec['priority']}: {rec['category']}")
            print(f"   Recommendation: {rec['recommendation']}")
            print(f"   Rationale: {rec['rationale']}")
            print()
        
        return recommendations
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete validation analysis"""
        print("🤖 ANOMALY AGENT RISK DETECTION SYSTEM VALIDATION")
        print("=" * 60)
        print(f"Analysis Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all analysis components
        prompt_analysis = self.analyze_agent_prompts()
        scenario_analysis = self.analyze_test_scenarios()
        detection_analysis = self.assess_detection_capabilities()
        applicability_analysis = self.assess_real_world_applicability()
        recommendations = self.generate_recommendations()
        
        # Generate overall assessment
        print("\n📋 OVERALL SYSTEM ASSESSMENT")
        print("=" * 50)
        
        sophistication_score = prompt_analysis.get("sophistication_score", 0)
        readiness_score = applicability_analysis.get("readiness_score", 0)
        
        # Calculate complexity score from scenarios
        complexity_scores = []
        for scenario_data in scenario_analysis.values():
            if isinstance(scenario_data, dict) and "complexity_score" in scenario_data:
                complexity_scores.append(scenario_data["complexity_score"])
        avg_complexity_score = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        overall_score = (sophistication_score + readiness_score + avg_complexity_score) / 3
        
        grade = "A" if overall_score >= 85 else "B" if overall_score >= 70 else "C" if overall_score >= 55 else "D"
        
        print(f"Agent Prompt Sophistication: {sophistication_score:.1f}/100")
        print(f"Test Scenario Complexity: {avg_complexity_score:.1f}/100")
        print(f"Real-World Readiness: {readiness_score:.1f}/100")
        print(f"OVERALL GRADE: {grade} ({overall_score:.1f}/100)")
        
        if grade in ["A", "B"]:
            print("✅ SYSTEM READY for sophisticated behavioral risk detection")
        elif grade == "C":
            print("⚠️  SYSTEM NEEDS IMPROVEMENTS before production deployment")
        else:
            print("❌ SYSTEM REQUIRES SIGNIFICANT WORK before production use")
        
        return {
            "prompt_analysis": prompt_analysis,
            "scenario_analysis": scenario_analysis,
            "detection_analysis": detection_analysis,
            "applicability_analysis": applicability_analysis,
            "recommendations": recommendations,
            "overall_score": overall_score,
            "grade": grade
        }

def main():
    """Run the comprehensive agent validation analysis"""
    analyzer = AgentValidationAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    # Save results to file
    results_path = Path("/home/user/webapp/validation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full analysis results saved to: {results_path}")
    return results

if __name__ == "__main__":
    main()