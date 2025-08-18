from typing import (
    Any,
    Dict,
    List,
)
import yaml
import re
import json

from src.agent.general_agent import GeneralAgent
from src.base.async_multistep_agent import PromptTemplates

from src.memory import AgentMemory
from src.models import Model
from src.registry import AGENT
from src.utils import assemble_project_path

@AGENT.register_module(name="behavioral_risk_coordinator_agent", force=True)
class BehavioralRiskCoordinatorAgent(GeneralAgent):
    def __init__(
            self,
            config,
            tools: list[Any],
            model: Model,
            prompt_templates: PromptTemplates | None = None,
            planning_interval: int | None = None,
            stream_outputs: bool = False,
            max_tool_threads: int | None = None,
            **kwargs,
    ):
        self.config = config

        super(BehavioralRiskCoordinatorAgent, self).__init__(
            config=config,
            tools=tools,
            model=model,
            prompt_templates=prompt_templates,
            planning_interval=planning_interval,
            **kwargs,
        )

        template_path = assemble_project_path(self.config.template_path)
        with open(template_path, "r") as f:
            self.prompt_templates = yaml.safe_load(f)

        self.system_prompt = self.initialize_system_prompt()
        self.user_prompt = self.initialize_user_prompt()

        # Streaming setup
        self.stream_outputs = stream_outputs
        if self.stream_outputs and not hasattr(self.model, "generate_stream"):
            raise ValueError(
                "`stream_outputs` is set to True, but the model class implements no `generate_stream` method."
            )
        # Tool calling setup
        self.max_tool_threads = max_tool_threads

        self.memory = AgentMemory(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
        )
        
        # Behavioral risk analysis state
        self.specialist_reports = {}
        self.risk_categories = [
            "goal_alignment",
            "purpose_deviation", 
            "deception_detection",
            "experience_quality"
        ]

    def aggregate_behavioral_risk_reports(self, reports: Dict[str, str]) -> Dict[str, Any]:
        """
        Aggregate specialist agent reports to make binary behavioral risk decision.
        
        Args:
            reports: Dictionary mapping agent names to their final answer reports
            
        Returns:
            Dictionary containing aggregated risk assessment
        """
        risk_detected = False
        detected_risks = []
        confidence_scores = []
        evidence_list = []
        
        for agent_name, report in reports.items():
            # Parse risk detection from report
            if self._extract_risk_detection(report):
                risk_detected = True
                detected_risks.append(agent_name)
            
            # Extract confidence score if available
            confidence = self._extract_confidence_score(report)
            if confidence is not None:
                confidence_scores.append(confidence)
                
            # Extract evidence
            evidence = self._extract_evidence(report)
            if evidence:
                evidence_list.extend(evidence)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        return {
            "behavioral_risk_detected": risk_detected,
            "detected_risk_categories": detected_risks,
            "overall_confidence": overall_confidence,
            "supporting_evidence": evidence_list,
            "specialist_reports": reports
        }
    
    def _extract_risk_detection(self, report: str) -> bool:
        """Extract binary risk detection from specialist report."""
        # Look for explicit risk indicators
        risk_patterns = [
            r"RISK DETECTED:\s*TRUE",
            r"BEHAVIORAL RISK:\s*TRUE", 
            r"RISK FOUND:\s*TRUE",
            r"ANOMALY DETECTED:\s*TRUE",
            r"HIGH RISK",
            r"CRITICAL RISK",
            r"SIGNIFICANT RISK"
        ]
        
        for pattern in risk_patterns:
            if re.search(pattern, report, re.IGNORECASE):
                return True
                
        return False
    
    def _extract_confidence_score(self, report: str) -> float | None:
        """Extract confidence score from specialist report."""
        # Look for confidence patterns
        confidence_patterns = [
            r"CONFIDENCE:\s*([0-9.]+)",
            r"CONFIDENCE LEVEL:\s*([0-9.]+)",
            r"CONFIDENCE SCORE:\s*([0-9.]+)"
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, report, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
                    
        return None
    
    def _extract_evidence(self, report: str) -> List[str]:
        """Extract evidence list from specialist report."""
        evidence = []
        
        # Look for evidence sections
        evidence_patterns = [
            r"EVIDENCE:\s*(.+?)(?:\n\n|\n###|\nRECOMMENDATIONS|$)",
            r"SUPPORTING EVIDENCE:\s*(.+?)(?:\n\n|\n###|\nRECOMMENDATIONS|$)"
        ]
        
        for pattern in evidence_patterns:
            match = re.search(pattern, report, re.IGNORECASE | re.DOTALL)
            if match:
                evidence_text = match.group(1).strip()
                # Split by bullet points or line breaks
                evidence_items = re.split(r'[•\-\*]\s*|(?:\n\s*)+', evidence_text)
                evidence.extend([item.strip() for item in evidence_items if item.strip()])
                
        return evidence
    
    def format_final_behavioral_risk_assessment(self, aggregated_results: Dict[str, Any]) -> str:
        """
        Format the final behavioral risk assessment following Skywork's final_answer pattern.
        
        Args:
            aggregated_results: Aggregated risk assessment results
            
        Returns:
            Formatted final assessment string
        """
        risk_status = "TRUE" if aggregated_results["behavioral_risk_detected"] else "FALSE"
        
        assessment = f"BEHAVIORAL RISK DETECTED: {risk_status}\n\n"
        
        if aggregated_results["behavioral_risk_detected"]:
            assessment += "RISK ANALYSIS:\n"
            assessment += f"- Detected risk categories: {', '.join(aggregated_results['detected_risk_categories'])}\n"
            assessment += f"- Overall confidence: {aggregated_results['overall_confidence']:.2f}\n\n"
            
            if aggregated_results["supporting_evidence"]:
                assessment += "SUPPORTING EVIDENCE:\n"
                for i, evidence in enumerate(aggregated_results["supporting_evidence"][:5], 1):
                    assessment += f"{i}. {evidence}\n"
                assessment += "\n"
        else:
            assessment += "RISK ANALYSIS:\n"
            assessment += "- No significant behavioral risks detected across all categories\n"
            assessment += f"- Analysis confidence: {aggregated_results['overall_confidence']:.2f}\n\n"
        
        assessment += "SPECIALIST AGENT REPORTS:\n"
        for agent_name, report in aggregated_results["specialist_reports"].items():
            assessment += f"\n{agent_name.upper()} REPORT:\n"
            # Include first 200 characters of each report
            report_summary = report[:200] + "..." if len(report) > 200 else report
            assessment += f"{report_summary}\n"
            
        return assessment