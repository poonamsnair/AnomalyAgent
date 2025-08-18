import json
import jsonlines
from typing import Any, Dict, List, Union
from datetime import datetime
from dataclasses import asdict

from src.tools.tools import AsyncTool, ToolResult
from src.registry import TOOL
from src.memory.memory import (
    ActionStep, PlanningStep, TaskStep, SystemPromptStep, FinalAnswerStep,
    ToolCall, AgentMemory
)
from src.models import ChatMessage, MessageRole
from src.logger import Timing, TokenUsage
from src.exception import AgentError


@TOOL.register_module(name="trajectory_parser_tool", force=True)
class TrajectoryParserTool(AsyncTool):
    name = "trajectory_parser_tool"
    description = "Parses agent trajectory data and converts to internal memory format for behavioral risk analysis. Supports JSON, JSONL, and Skywork trajectory formats."
    parameters = {
        "type": "object",
        "properties": {
            "trajectory_data": {
                "type": "string",
                "description": "Raw trajectory data in JSON/JSONL format or file path to trajectory file",
            },
            "format_type": {
                "type": "string", 
                "description": "Input format type: 'json', 'jsonl', or 'skywork'",
                "enum": ["json", "jsonl", "skywork"]
            },
        },
        "required": ["trajectory_data", "format_type"],
    }
    output_type = "string"

    async def forward(self, trajectory_data: str, format_type: str) -> ToolResult:
        """
        Parse trajectory data and convert to Skywork memory format.
        
        Args:
            trajectory_data: Raw trajectory data or file path
            format_type: Format type ('json', 'jsonl', 'skywork')
            
        Returns:
            ToolResult with parsed trajectory in Skywork memory format
        """
        try:
            # Validate inputs
            validation_error = self._validate_inputs(trajectory_data, format_type)
            if validation_error:
                return ToolResult(output=None, error=validation_error)

            # Parse the trajectory data based on format
            if format_type == "json":
                parsed_trajectory = self._parse_json_trajectory(trajectory_data)
            elif format_type == "jsonl":
                parsed_trajectory = self._parse_jsonl_trajectory(trajectory_data)
            elif format_type == "skywork":
                parsed_trajectory = self._parse_skywork_trajectory(trajectory_data)

            # Validate parsed trajectory structure
            validation_error = self._validate_trajectory_structure(parsed_trajectory)
            if validation_error:
                return ToolResult(output=None, error=validation_error)

            # Convert to Skywork memory format
            agent_memory = self._convert_to_skywork_memory(parsed_trajectory)
            
            # Validate converted memory
            validation_error = self._validate_converted_memory(agent_memory)
            if validation_error:
                return ToolResult(output=None, error=validation_error)
            
            # Return serialized memory for analysis
            result = {
                "trajectory_id": parsed_trajectory.get("trajectory_id", "unknown"),
                "agent_name": parsed_trajectory.get("agent_name", "unknown"),
                "task_description": parsed_trajectory.get("task_description", ""),
                "memory_steps": agent_memory.get_full_steps(),
                "system_prompt": agent_memory.system_prompt.system_prompt if agent_memory.system_prompt else None,
                "user_prompt": agent_memory.user_prompt.user_prompt if agent_memory.user_prompt else None,
                "step_count": len(agent_memory.steps),
                "parsing_status": "success",
                "validation_warnings": self._get_validation_warnings(parsed_trajectory, agent_memory)
            }

            return ToolResult(
                output=json.dumps(result, indent=2),
                error=None
            )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Error parsing trajectory: {str(e)}"
            )

    def _validate_inputs(self, trajectory_data: str, format_type: str) -> str:
        """Validate input parameters."""
        if not trajectory_data or not isinstance(trajectory_data, str):
            return "trajectory_data must be a non-empty string"
        
        if format_type not in ["json", "jsonl", "skywork"]:
            return f"Invalid format_type '{format_type}'. Must be one of: json, jsonl, skywork"
        
        if len(trajectory_data.strip()) == 0:
            return "trajectory_data cannot be empty or whitespace only"
            
        return None

    def _validate_trajectory_structure(self, trajectory: Dict[str, Any]) -> str:
        """Validate the structure of parsed trajectory data."""
        if not isinstance(trajectory, dict):
            return "Trajectory must be a dictionary"
        
        # Check for required fields
        required_fields = ["trajectory_id", "steps"]
        for field in required_fields:
            if field not in trajectory:
                return f"Missing required field: {field}"
        
        # Validate steps
        steps = trajectory.get("steps", [])
        if not isinstance(steps, list):
            return "Steps must be a list"
        
        if len(steps) == 0:
            return "Trajectory must contain at least one step"
        
        # Validate each step
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                return f"Step {i + 1} must be a dictionary"
            
            # Check for basic step structure
            if "step_type" not in step and "type" not in step and "content" not in step:
                return f"Step {i + 1} missing step_type, type, or content field"
        
        return None

    def _validate_converted_memory(self, memory: AgentMemory) -> str:
        """Validate the converted AgentMemory object."""
        if not isinstance(memory, AgentMemory):
            return "Converted memory must be an AgentMemory instance"
        
        if not memory.system_prompt:
            return "Memory must have a system prompt"
        
        if not isinstance(memory.steps, list):
            return "Memory steps must be a list"
        
        # Validate step types
        valid_step_types = (ActionStep, PlanningStep, TaskStep)
        for i, step in enumerate(memory.steps):
            if not isinstance(step, valid_step_types):
                return f"Step {i + 1} has invalid type: {type(step)}"
        
        return None

    def _get_validation_warnings(self, trajectory: Dict[str, Any], memory: AgentMemory) -> List[str]:
        """Generate validation warnings for potential issues."""
        warnings = []
        
        # Check for missing optional fields
        if not trajectory.get("agent_name") or trajectory.get("agent_name") == "unknown":
            warnings.append("Agent name is missing or unknown")
        
        if not trajectory.get("task_description"):
            warnings.append("Task description is missing")
        
        if not trajectory.get("system_prompt"):
            warnings.append("System prompt is missing")
        
        # Check step quality
        steps = trajectory.get("steps", [])
        action_steps = [s for s in steps if s.get("step_type", s.get("type")) == "action"]
        
        if len(action_steps) == 0:
            warnings.append("No action steps found in trajectory")
        
        # Check for steps with errors
        error_steps = [s for s in steps if "error" in s and s["error"]]
        if error_steps:
            warnings.append(f"Found {len(error_steps)} steps with errors")
        
        # Check for incomplete steps
        incomplete_steps = []
        for i, step in enumerate(steps):
            if not step.get("content") and not step.get("model_output") and not step.get("observations"):
                incomplete_steps.append(i + 1)
        
        if incomplete_steps:
            warnings.append(f"Steps {incomplete_steps} appear to be incomplete (missing content/output)")
        
        return warnings

    def _parse_json_trajectory(self, trajectory_data: str) -> Dict[str, Any]:
        """Parse JSON format trajectory data with comprehensive error handling."""
        data = None
        
        try:
            # Try to parse as JSON string first
            data = json.loads(trajectory_data)
        except json.JSONDecodeError as json_error:
            # If that fails, try to read as file path
            try:
                import os
                if os.path.isfile(trajectory_data):
                    with open(trajectory_data, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    raise FileNotFoundError(f"File not found: {trajectory_data}")
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as file_error:
                raise ValueError(
                    f"Failed to parse JSON trajectory. "
                    f"JSON parse error: {str(json_error)}. "
                    f"File read error: {str(file_error)}"
                )

        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError(f"JSON trajectory must be a dictionary, got {type(data)}")

        # Check for malformed data
        if not data:
            raise ValueError("JSON trajectory is empty")

        return self._normalize_trajectory_data(data)

    def _parse_jsonl_trajectory(self, trajectory_data: str) -> Dict[str, Any]:
        """Parse JSONL format trajectory data with comprehensive error handling."""
        steps = []
        parse_errors = []
        
        try:
            # Try to parse as JSONL string first
            lines = trajectory_data.strip().split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        step_data = json.loads(line)
                        steps.append(step_data)
                    except json.JSONDecodeError as e:
                        parse_errors.append(f"Line {line_num}: {str(e)}")
                        
        except Exception as string_error:
            # If string parsing fails, try to read as file path
            try:
                import os
                if os.path.isfile(trajectory_data):
                    with jsonlines.open(trajectory_data) as reader:
                        for line_num, obj in enumerate(reader, 1):
                            try:
                                steps.append(obj)
                            except Exception as e:
                                parse_errors.append(f"Line {line_num}: {str(e)}")
                else:
                    raise FileNotFoundError(f"File not found: {trajectory_data}")
            except (FileNotFoundError, PermissionError, jsonlines.InvalidLineError) as file_error:
                raise ValueError(
                    f"Failed to parse JSONL trajectory. "
                    f"String parse error: {str(string_error)}. "
                    f"File read error: {str(file_error)}"
                )

        # Report parsing errors but continue if we have some valid steps
        if parse_errors:
            if not steps:
                raise ValueError(f"No valid JSONL steps found. Errors: {'; '.join(parse_errors)}")
            else:
                print(f"Warning: Some JSONL lines failed to parse: {'; '.join(parse_errors)}")

        if not steps:
            raise ValueError("JSONL trajectory contains no valid steps")

        # Extract metadata from first step if available
        first_step = steps[0] if steps else {}
        trajectory_id = first_step.get("trajectory_id", f"jsonl_{datetime.now().isoformat()}")
        agent_name = first_step.get("agent_name", "unknown")
        task_description = first_step.get("task_description", "")

        # Convert JSONL steps to trajectory format
        trajectory = {
            "trajectory_id": trajectory_id,
            "agent_name": agent_name,
            "task_description": task_description,
            "steps": steps,
            "metadata": {"parse_errors": parse_errors} if parse_errors else {}
        }

        return self._normalize_trajectory_data(trajectory)

    def _parse_skywork_trajectory(self, trajectory_data: str) -> Dict[str, Any]:
        """Parse Skywork format trajectory data with validation."""
        data = None
        
        try:
            # Try to parse as JSON string first
            data = json.loads(trajectory_data)
        except json.JSONDecodeError as json_error:
            # If that fails, try to read as file path
            try:
                import os
                if os.path.isfile(trajectory_data):
                    with open(trajectory_data, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    raise FileNotFoundError(f"File not found: {trajectory_data}")
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as file_error:
                raise ValueError(
                    f"Failed to parse Skywork trajectory. "
                    f"JSON parse error: {str(json_error)}. "
                    f"File read error: {str(file_error)}"
                )

        # Validate Skywork format structure
        if not isinstance(data, dict):
            raise ValueError(f"Skywork trajectory must be a dictionary, got {type(data)}")

        if not data:
            raise ValueError("Skywork trajectory is empty")

        # Validate Skywork-specific fields
        expected_skywork_fields = ["memory_steps", "system_prompt"]
        has_skywork_fields = any(field in data for field in expected_skywork_fields)
        
        if not has_skywork_fields:
            # If it doesn't look like Skywork format, try to normalize it
            print("Warning: Data doesn't appear to be in Skywork format, attempting to normalize")
            return self._normalize_trajectory_data(data)

        return data

    def _normalize_trajectory_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize trajectory data to standard format."""
        normalized = {
            "trajectory_id": data.get("trajectory_id", data.get("id", f"traj_{datetime.now().isoformat()}")),
            "agent_name": data.get("agent_name", data.get("agent", "unknown")),
            "task_description": data.get("task_description", data.get("task", data.get("description", ""))),
            "start_time": data.get("start_time", datetime.now().isoformat()),
            "end_time": data.get("end_time", datetime.now().isoformat()),
            "steps": data.get("steps", []),
            "metadata": data.get("metadata", {}),
            "system_prompt": data.get("system_prompt", ""),
            "user_prompt": data.get("user_prompt", "")
        }

        return normalized

    def _convert_to_skywork_memory(self, trajectory_data: Dict[str, Any]) -> AgentMemory:
        """Convert normalized trajectory data to Skywork AgentMemory format with error handling."""
        # Initialize memory with system prompt
        system_prompt = trajectory_data.get("system_prompt", "Behavioral risk analysis system")
        user_prompt = trajectory_data.get("user_prompt")
        
        try:
            memory = AgentMemory(system_prompt=system_prompt, user_prompt=user_prompt)
        except Exception as e:
            raise ValueError(f"Failed to initialize AgentMemory: {str(e)}")

        # Process each step in the trajectory
        conversion_errors = []
        successful_conversions = 0
        
        for i, step_data in enumerate(trajectory_data.get("steps", [])):
            try:
                memory_step = self._convert_step_to_memory(step_data, i + 1)
                if memory_step:
                    memory.steps.append(memory_step)
                    successful_conversions += 1
                else:
                    conversion_errors.append(f"Step {i + 1}: Conversion returned None")
            except Exception as e:
                conversion_errors.append(f"Step {i + 1}: {str(e)}")
                continue

        # Report conversion issues
        if conversion_errors:
            error_summary = f"Conversion errors for {len(conversion_errors)} steps: {'; '.join(conversion_errors[:5])}"
            if len(conversion_errors) > 5:
                error_summary += f" ... and {len(conversion_errors) - 5} more"
            print(f"Warning: {error_summary}")

        if successful_conversions == 0:
            raise ValueError("Failed to convert any steps to memory format")

        return memory

    def _convert_step_to_memory(self, step_data: Dict[str, Any], step_number: int) -> Union[ActionStep, PlanningStep, TaskStep, None]:
        """Convert a single step to appropriate memory step type with error handling."""
        if not isinstance(step_data, dict):
            raise ValueError(f"Step data must be a dictionary, got {type(step_data)}")
        
        step_type = step_data.get("step_type", step_data.get("type", "action"))
        
        # Create timing information with error handling
        try:
            start_time_str = step_data.get("timestamp", step_data.get("start_time", datetime.now().isoformat()))
            end_time_str = step_data.get("end_timestamp", step_data.get("end_time", datetime.now().isoformat()))
            
            # Handle various timestamp formats
            start_time = self._parse_timestamp(start_time_str)
            end_time = self._parse_timestamp(end_time_str)
            
            timing = Timing(start_time=start_time, end_time=end_time)
        except Exception as e:
            # Fallback to current time if timestamp parsing fails
            now = datetime.now()
            timing = Timing(start_time=now, end_time=now)
            print(f"Warning: Failed to parse timestamps for step {step_number}, using current time: {str(e)}")

        # Create token usage if available
        token_usage = None
        if "token_usage" in step_data:
            try:
                token_data = step_data["token_usage"]
                if isinstance(token_data, dict):
                    token_usage = TokenUsage(
                        prompt_tokens=int(token_data.get("prompt_tokens", 0)),
                        completion_tokens=int(token_data.get("completion_tokens", 0)),
                        total_tokens=int(token_data.get("total_tokens", 0))
                    )
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to parse token usage for step {step_number}: {str(e)}")

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string with multiple format support."""
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        
        if not isinstance(timestamp_str, str):
            timestamp_str = str(timestamp_str)
        
        # Try different timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%dT%H:%M:%S",     # ISO format without microseconds
            "%Y-%m-%d %H:%M:%S.%f",  # Space-separated with microseconds
            "%Y-%m-%d %H:%M:%S",     # Space-separated without microseconds
            "%Y-%m-%d",              # Date only
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, try fromisoformat
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            # Last resort: return current time
            return datetime.now()

        if step_type == "task":
            return TaskStep(
                task=step_data.get("content", step_data.get("task", "")),
                task_images=None  # Images not supported in this basic implementation
            )

        elif step_type == "planning":
            # Create model messages
            model_input_messages = self._convert_messages(step_data.get("model_input_messages", []))
            model_output_message = self._convert_message(step_data.get("model_output_message", {}))
            
            return PlanningStep(
                model_input_messages=model_input_messages,
                model_output_message=model_output_message,
                plan=step_data.get("plan", step_data.get("content", "")),
                timing=timing,
                token_usage=token_usage
            )

        elif step_type == "action":
            # Convert tool calls
            tool_calls = []
            if "tool_calls" in step_data:
                for tc_data in step_data["tool_calls"]:
                    tool_call = ToolCall(
                        name=tc_data.get("function", {}).get("name", tc_data.get("name", "")),
                        arguments=tc_data.get("function", {}).get("arguments", tc_data.get("arguments", {})),
                        id=tc_data.get("id", f"call_{step_number}")
                    )
                    tool_calls.append(tool_call)

            # Handle errors
            error = None
            if "error" in step_data:
                error_data = step_data["error"]
                error = AgentError(error_data.get("message", str(error_data)))

            # Create model messages
            model_input_messages = self._convert_messages(step_data.get("model_input_messages", []))
            model_output_message = self._convert_message(step_data.get("model_output_message", {}))

            return ActionStep(
                step_number=step_number,
                timing=timing,
                model_input_messages=model_input_messages,
                tool_calls=tool_calls if tool_calls else None,
                error=error,
                model_output_message=model_output_message,
                model_output=step_data.get("model_output", step_data.get("content")),
                observations=step_data.get("observations", step_data.get("observation")),
                observations_images=None,  # Images not supported in basic implementation
                action_output=step_data.get("action_output", step_data.get("output")),
                token_usage=token_usage,
                is_final_answer=step_data.get("is_final_answer", False)
            )

        elif step_type == "anomaly_detection" or step_type == "behavioral_risk":
            # Create ActionStep for behavioral risk analysis (AnomalyDetectionStep not available)
            tool_calls = []
            if "tool_calls" in step_data:
                for tc_data in step_data["tool_calls"]:
                    tool_call = ToolCall(
                        name=tc_data.get("function", {}).get("name", tc_data.get("name", "")),
                        arguments=tc_data.get("function", {}).get("arguments", tc_data.get("arguments", {})),
                        id=tc_data.get("id", f"call_{step_number}")
                    )
                    tool_calls.append(tool_call)

            error = None
            if "error" in step_data:
                error_data = step_data["error"]
                error = AgentError(error_data.get("message", str(error_data)))

            model_input_messages = self._convert_messages(step_data.get("model_input_messages", []))
            model_output_message = self._convert_message(step_data.get("model_output_message", {}))

            return ActionStep(
                step_number=step_number,
                timing=timing,
                model_input_messages=model_input_messages,
                tool_calls=tool_calls if tool_calls else None,
                error=error,
                model_output_message=model_output_message,
                model_output=step_data.get("model_output", step_data.get("content")),
                observations=step_data.get("observations", step_data.get("observation")),
                observations_images=None,
                action_output=step_data.get("action_output", step_data.get("output")),
                token_usage=token_usage,
                is_final_answer=step_data.get("is_final_answer", False)
            )

        else:
            # Default to ActionStep for unknown types
            return ActionStep(
                step_number=step_number,
                timing=timing,
                model_input_messages=[],
                tool_calls=None,
                error=None,
                model_output_message=None,
                model_output=step_data.get("content", ""),
                observations=None,
                observations_images=None,
                action_output=None,
                token_usage=token_usage,
                is_final_answer=False
            )

    def _convert_messages(self, messages_data: List[Dict[str, Any]]) -> List[ChatMessage]:
        """Convert message data to ChatMessage objects."""
        messages = []
        for msg_data in messages_data:
            message = self._convert_message(msg_data)
            if message:
                messages.append(message)
        return messages

    def _convert_message(self, msg_data: Dict[str, Any]) -> ChatMessage:
        """Convert single message data to ChatMessage object."""
        if not msg_data:
            return None

        role_str = msg_data.get("role", "user")
        
        # Map role strings to MessageRole enum
        role_mapping = {
            "system": MessageRole.SYSTEM,
            "user": MessageRole.USER,
            "assistant": MessageRole.ASSISTANT,
            "tool": MessageRole.TOOL_RESPONSE,
            "tool_call": MessageRole.TOOL_CALL,
            "tool_response": MessageRole.TOOL_RESPONSE
        }
        
        role = role_mapping.get(role_str.lower(), MessageRole.USER)
        
        # Handle content - can be string or list
        content = msg_data.get("content", "")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        elif not isinstance(content, list):
            content = [{"type": "text", "text": str(content)}]

        return ChatMessage(role=role, content=content)