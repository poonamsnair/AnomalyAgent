#!/usr/bin/env python3
"""
Agent Trace Reference Tool

This tool allows agents to reference optimal execution paths and performance benchmarks
for behavioral risk analysis. It provides guidance on best practices, expected timing,
and execution strategies.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.tools.tools import AsyncTool, ToolResult
from src.registry import TOOL
from src.logger import logger


@TOOL.register_module(name="agent_trace_reference_tool", force=True)
class AgentTraceReferenceTool(AsyncTool):
    """
    Tool for agents to reference optimal execution traces and best practices.
    
    This tool provides:
    - Reference execution paths for behavioral risk analysis
    - Performance benchmarks and timing expectations
    - Best practice guidance for agent coordination
    - Execution strategy recommendations based on confidence levels
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "agent_trace_reference_tool"
        self.description = "Reference tool for optimal agent execution paths and performance benchmarks in behavioral risk analysis"
        
        # Load the trace reference data
        self.trace_file_path = Path(__file__).parent / "agent_trace_reference.json"
        self.trace_data = self._load_trace_data()
        
    def _load_trace_data(self) -> Dict[str, Any]:
        """Load the agent trace reference data from JSON file."""
        try:
            with open(self.trace_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load agent trace reference: {e}")
            return {}
    
    def get_optimal_path(self, use_case: str = "default") -> List[Dict[str, Any]]:
        """
        Get the optimal execution path for a specific use case.
        
        Args:
            use_case: The use case to get the path for (default: "default")
            
        Returns:
            List of steps in the optimal execution path
        """
        if not self.trace_data:
            return []
            
        return self.trace_data.get("optimal_agent_path", [])
    
    def get_performance_benchmarks(self) -> Dict[str, Any]:
        """
        Get performance benchmarks and timing expectations.
        
        Returns:
            Dictionary containing performance metrics and benchmarks
        """
        if not self.trace_data:
            return {}
            
        return self.trace_data.get("performance_metrics", {})
    
    def get_execution_strategy(self, confidence_level: float, risk_indicators: int = 0) -> Dict[str, Any]:
        """
        Get recommended execution strategy based on confidence level and risk indicators.
        
        Args:
            confidence_level: Current confidence level (0.0 to 1.0)
            risk_indicators: Number of risk indicators detected
            
        Returns:
            Dictionary containing recommended execution strategy
        """
        if not self.trace_data:
            return {"strategy": "unknown", "reason": "No trace data available"}
        
        execution_modes = self.trace_data.get("execution_modes", {})
        
        # Determine strategy based on confidence and risk indicators
        if confidence_level >= 0.8 and risk_indicators == 0:
            strategy_info = execution_modes.get("high_confidence_early_return", {})
            strategy_info["recommended_strategy"] = "early_return"
        else:
            strategy_info = execution_modes.get("parallel_full_analysis", {})
            strategy_info["recommended_strategy"] = "full_parallel_analysis"
            
        return strategy_info
    
    def get_step_guidance(self, step_number: int) -> Dict[str, Any]:
        """
        Get guidance for a specific step in the execution path.
        
        Args:
            step_number: The step number to get guidance for
            
        Returns:
            Dictionary containing step-specific guidance
        """
        optimal_path = self.get_optimal_path()
        
        for step in optimal_path:
            if step.get("step") == step_number:
                return step
                
        return {}
    
    def get_agent_guidance(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Get guidance specific to a particular agent.
        
        Args:
            agent_name: Name of the agent to get guidance for
            
        Returns:
            List of steps where this agent is involved
        """
        optimal_path = self.get_optimal_path()
        agent_steps = []
        
        for step in optimal_path:
            if step.get("agent") == agent_name:
                agent_steps.append(step)
                
        return agent_steps
    
    async def __call__(self, 
                       query_type: str = "optimal_path",
                       agent_name: Optional[str] = None,
                       step_number: Optional[int] = None,
                       confidence_level: Optional[float] = None,
                       risk_indicators: Optional[int] = None) -> ToolResult:
        """
        Main tool interface for querying trace reference information.
        
        Args:
            query_type: Type of query ("optimal_path", "performance", "strategy", "step_guidance", "agent_guidance")
            agent_name: Name of specific agent (for agent_guidance query)
            step_number: Specific step number (for step_guidance query)
            confidence_level: Current confidence level (for strategy query)
            risk_indicators: Number of risk indicators (for strategy query)
            
        Returns:
            JSON string containing the requested information
        """
        try:
            if query_type == "optimal_path":
                result = self.get_optimal_path()
                
            elif query_type == "performance":
                result = self.get_performance_benchmarks()
                
            elif query_type == "strategy":
                if confidence_level is None:
                    confidence_level = 0.5
                if risk_indicators is None:
                    risk_indicators = 0
                result = self.get_execution_strategy(confidence_level, risk_indicators)
                
            elif query_type == "step_guidance":
                if step_number is None:
                    return json.dumps({"error": "step_number required for step_guidance query"})
                result = self.get_step_guidance(step_number)
                
            elif query_type == "agent_guidance":
                if agent_name is None:
                    return json.dumps({"error": "agent_name required for agent_guidance query"})
                result = self.get_agent_guidance(agent_name)
                
            else:
                result = {
                    "error": f"Unknown query_type: {query_type}",
                    "available_types": ["optimal_path", "performance", "strategy", "step_guidance", "agent_guidance"]
                }
            
            return ToolResult(content=json.dumps(result, indent=2))
            
        except Exception as e:
            logger.error(f"Error in agent_trace_reference_tool: {e}")
            return ToolResult(content=json.dumps({"error": str(e)}), error=str(e))


# Tool parameters schema for OpenAI-compatible function calling
TOOL_PARAMETERS = {
    "type": "object",
    "properties": {
        "query_type": {
            "type": "string",
            "enum": ["optimal_path", "performance", "strategy", "step_guidance", "agent_guidance"],
            "description": "Type of trace reference query to perform"
        },
        "agent_name": {
            "type": "string",
            "description": "Name of specific agent (for agent_guidance query)"
        },
        "step_number": {
            "type": "integer",
            "description": "Specific step number (for step_guidance query)"
        },
        "confidence_level": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Current confidence level (for strategy query)"
        },
        "risk_indicators": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of risk indicators detected (for strategy query)"
        }
    },
    "required": ["query_type"]
}


if __name__ == "__main__":
    # Test the tool
    tool = AgentTraceReferenceTool()
    
    # Test optimal path query
    print("=== Optimal Path ===")
    result = tool(query_type="optimal_path")
    print(result)
    
    # Test performance benchmarks
    print("\n=== Performance Benchmarks ===")
    result = tool(query_type="performance")
    print(result)
    
    # Test execution strategy
    print("\n=== Execution Strategy (High Confidence) ===")
    result = tool(query_type="strategy", confidence_level=0.9, risk_indicators=0)
    print(result)
    
    # Test execution strategy
    print("\n=== Execution Strategy (Low Confidence) ===")
    result = tool(query_type="strategy", confidence_level=0.5, risk_indicators=2)
    print(result)