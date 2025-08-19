#!/usr/bin/env python3
"""
Enhanced logging and streaming functionality for AnomalyAgent
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator
from pathlib import Path

class RiskDetectionLogger:
    """Enhanced logger for risk detection events with streaming capability"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files for different types of events
        self.risk_log_file = self.log_dir / "risk_detections.jsonl"
        self.session_log_file = self.log_dir / "session_events.jsonl"
        self.agent_log_file = self.log_dir / "agent_activities.jsonl"
    
    def log_risk_detection(self, session_id: str, step_number: int, 
                          risk_assessment: Dict[str, Any], 
                          agent_reports: Dict[str, Any] = None):
        """Log a risk detection event with detailed information"""
        
        risk_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "risk_detection",
            "session_id": session_id,
            "step_number": step_number,
            "risk_detected": risk_assessment.get("risk_detected", False),
            "confidence_score": risk_assessment.get("confidence_score", 0.0),
            "risk_categories": risk_assessment.get("risk_categories", []),
            "evidence": risk_assessment.get("evidence", []),
            "context_window_size": risk_assessment.get("context_window_size", 0),
            "assessment_timestamp": risk_assessment.get("assessment_timestamp"),
            "agent_reports": agent_reports or {}
        }
        
        # Write to risk detection log
        with open(self.risk_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(risk_event) + "\n")
        
        return risk_event
    
    def log_agent_activity(self, agent_name: str, session_id: str, 
                          activity: str, details: Dict[str, Any] = None):
        """Log individual agent activity"""
        
        agent_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "agent_activity", 
            "agent_name": agent_name,
            "session_id": session_id,
            "activity": activity,
            "details": details or {}
        }
        
        with open(self.agent_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(agent_event) + "\n")
        
        return agent_event
    
    def log_session_event(self, session_id: str, event_type: str, 
                         details: Dict[str, Any] = None):
        """Log session-level events"""
        
        session_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": f"session_{event_type}",
            "session_id": session_id,
            "details": details or {}
        }
        
        with open(self.session_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(session_event) + "\n")
        
        return session_event
    
    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all logs for a specific session"""
        session_logs = []
        
        # Read from all log files
        for log_file in [self.risk_log_file, self.session_log_file, self.agent_log_file]:
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            if event.get("session_id") == session_id:
                                session_logs.append(event)
                        except json.JSONDecodeError:
                            continue
        
        # Sort by timestamp
        session_logs.sort(key=lambda x: x.get("timestamp", ""))
        return session_logs
    
    def get_risk_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get a summary of risk detections"""
        risk_events = []
        
        if self.risk_log_file.exists():
            with open(self.risk_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if session_id is None or event.get("session_id") == session_id:
                            risk_events.append(event)
                    except json.JSONDecodeError:
                        continue
        
        total_assessments = len(risk_events)
        risk_detections = [e for e in risk_events if e.get("risk_detected")]
        
        # Aggregate by risk categories
        risk_categories = {}
        for event in risk_detections:
            for category in event.get("risk_categories", []):
                risk_categories[category] = risk_categories.get(category, 0) + 1
        
        return {
            "total_assessments": total_assessments,
            "total_risks_detected": len(risk_detections),
            "risk_detection_rate": len(risk_detections) / max(1, total_assessments),
            "risk_categories": risk_categories,
            "session_id": session_id
        }

class StreamingAssessment:
    """Handles streaming of assessment progress"""
    
    def __init__(self, session_id: str, logger: RiskDetectionLogger):
        self.session_id = session_id
        self.logger = logger
        self.events = []
    
    async def stream_assessment_progress(self, step_data: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream assessment progress in real-time"""
        
        # Initial event
        yield {
            "event": "assessment_started",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "step_number": step_data.get("step_number"),
            "step_type": step_data.get("step_type")
        }
        
        # Simulate agent coordination phases
        agents = [
            "behavioral_risk_coordinator",
            "goal_alignment_agent", 
            "purpose_deviation_agent",
            "deception_detection_agent",
            "experience_quality_agent"
        ]
        
        for agent in agents:
            yield {
                "event": "agent_processing",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "agent_name": agent,
                "status": "analyzing"
            }
            
            # Small delay to simulate processing
            await asyncio.sleep(0.5)
            
            yield {
                "event": "agent_completed",
                "timestamp": datetime.now().isoformat(), 
                "session_id": self.session_id,
                "agent_name": agent,
                "status": "completed"
            }
        
        yield {
            "event": "assessment_integrating",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "status": "integrating_results"
        }

# Global logger instance
risk_logger = RiskDetectionLogger()