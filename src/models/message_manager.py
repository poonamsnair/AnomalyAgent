from typing import Dict, List, Optional, Any
from copy import deepcopy

from AnomalyAgent.src.models.base import MessageRole, ChatMessage
from AnomalyAgent.src.utils import encode_image_base64, make_image_url

DEFAULT_ANTHROPIC_MODELS = [
    'claude37-sonnet',
    "claude37-sonnet-thinking",
]
UNSUPPORTED_STOP_MODELS = [
    'claude37-sonnet',
    'o4-mini',
    'o3',
    'langchain-o3'
]
UNSUPPORTED_TOOL_CHOICE_MODELS = [
    'claude37-sonnet',
]

class MessageManager():
    def __init__(self, model_id: str, api_type: str = "chat/completions"):
        self.model_id = model_id
        self.api_type = api_type

    def get_clean_message_list(self,
            message_list: list[ChatMessage],
            role_conversions: dict[MessageRole, MessageRole] | dict[str, str] = {},
            convert_images_to_image_urls: bool = False,
            flatten_messages_as_text: bool = False,
            api_type: str = "chat/completions",
    ) -> list[dict[str, Any]]:
        """
        Creates a list of messages to give as input to the LLM. These messages are dictionaries and chat template compatible with transformers LLM chat template.
        Subsequent messages with the same role will be concatenated to a single message.

        Args:
            message_list (`list[dict[str, str]]`): List of chat messages.
            role_conversions (`dict[MessageRole, MessageRole]`, *optional* ): Mapping to convert roles.
            convert_images_to_image_urls (`bool`, default `False`): Whether to convert images to image URLs.
            flatten_messages_as_text (`bool`, default `False`): Whether to flatten messages as text.
        """
        api_type = api_type or self.api_type
        if api_type == "responses":
            return self._get_responses_message_list(
                message_list, role_conversions, convert_images_to_image_urls, flatten_messages_as_text
            )
        else:
            return self._get_chat_completions_message_list(
                message_list, role_conversions, convert_images_to_image_urls, flatten_messages_as_text
            )

    def _get_chat_completions_message_list(self,
            message_list: list[ChatMessage],
            role_conversions: dict[MessageRole, MessageRole] | dict[str, str] = {},
            convert_images_to_image_urls: bool = False,
            flatten_messages_as_text: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Creates a list of messages in chat completions format.
        """
        output_message_list: list[dict[str, Any]] = []
        message_list = deepcopy(message_list)  # Avoid modifying the original list
        for message in message_list:
            role = message.role
            if role not in MessageRole.roles():
                raise ValueError(f"Incorrect role {role}, only {MessageRole.roles()} are supported for now.")

            if role in role_conversions:
                message.role = role_conversions[role]  # type: ignore
            # encode images if needed
            if isinstance(message.content, list):
                for element in message.content:
                    assert isinstance(element, dict), "Error: this element should be a dict:" + str(element)
                    if element["type"] == "image":
                        assert not flatten_messages_as_text, f"Cannot use images with {flatten_messages_as_text=}"
                        if convert_images_to_image_urls:
                            element.update(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": make_image_url(encode_image_base64(element.pop("image")))},
                                }
                            )
                        else:
                            element["image"] = encode_image_base64(element["image"])

            if len(output_message_list) > 0 and message.role == output_message_list[-1]["role"]:
                assert isinstance(message.content, list), "Error: wrong content:" + str(message.content)
                if flatten_messages_as_text:
                    output_message_list[-1]["content"] += "\n" + message.content[0]["text"]
                else:
                    for el in message.content:
                        if el["type"] == "text" and output_message_list[-1]["content"][-1]["type"] == "text":
                            # Merge consecutive text messages rather than creating new ones
                            output_message_list[-1]["content"][-1]["text"] += "\n" + el["text"]
                        else:
                            output_message_list[-1]["content"].append(el)
            else:
                if flatten_messages_as_text:
                    content = message.content[0]["text"]
                else:
                    content = message.content
                output_message_list.append(
                    {
                        "role": message.role,
                        "content": content,
                    }
                )
        return output_message_list

    def _get_responses_message_list(self,
            message_list: list[ChatMessage],
            role_conversions: dict[MessageRole, MessageRole] | dict[str, str] = {},
            convert_images_to_image_urls: bool = False,
            flatten_messages_as_text: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Creates a list of messages in responses format (OpenAI responses API).
        """
        output_message_list: list[dict[str, Any]] = []
        message_list = deepcopy(message_list)  # Avoid modifying the original list
        
        for message in message_list:
            role = message.role
            if role not in MessageRole.roles():
                raise ValueError(f"Incorrect role {role}, only {MessageRole.roles()} are supported for now.")

            if role in role_conversions:
                message.role = role_conversions[role]  # type: ignore
            
            # Handle content processing
            if isinstance(message.content, list):
                # Process each content element
                processed_content = []
                for element in message.content:
                    assert isinstance(element, dict), "Error: this element should be a dict:" + str(element)
                    
                    if element["type"] == "image":
                        assert not flatten_messages_as_text, f"Cannot use images with {flatten_messages_as_text=}"
                        if convert_images_to_image_urls:
                            processed_content.append({
                                "type": "image_url",
                                "image_url": {"url": make_image_url(encode_image_base64(element.pop("image")))},
                            })
                        else:
                            processed_content.append({
                                "type": "image",
                                "image": encode_image_base64(element["image"])
                            })
                    elif element["type"] == "text":
                        processed_content.append(element)
                    else:
                        processed_content.append(element)
                
                content = processed_content
            else:
                # Handle string content
                if flatten_messages_as_text:
                    content = message.content
                else:
                    content = [{"type": "text", "text": message.content}] if message.content else []

            # Handle tool calls for responses format
            tool_calls = None
            if message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                            "description": tool_call.function.description
                        }
                    })

            # Create message in responses format
            message_dict = {
                "role": message.role,
                "content": content,
            }
            
            if tool_calls:
                message_dict["tool_calls"] = tool_calls

            # Merge consecutive messages with same role
            if len(output_message_list) > 0 and message.role == output_message_list[-1]["role"]:
                if flatten_messages_as_text:
                    if isinstance(content, list) and content and content[0]["type"] == "text":
                        output_message_list[-1]["content"] += "\n" + content[0]["text"]
                    else:
                        output_message_list[-1]["content"] += "\n" + str(content)
                else:
                    # Merge content lists
                    if isinstance(output_message_list[-1]["content"], list) and isinstance(content, list):
                        output_message_list[-1]["content"].extend(content)
                    else:
                        output_message_list[-1]["content"] = content
                
                # Merge tool calls
                if tool_calls and "tool_calls" in output_message_list[-1]:
                    output_message_list[-1]["tool_calls"].extend(tool_calls)
                elif tool_calls:
                    output_message_list[-1]["tool_calls"] = tool_calls
            else:
                output_message_list.append(message_dict)

        return output_message_list

    def get_tool_json_schema(self,
                             tool: Any,
                             model_id: Optional[str] = None
                             ) -> Dict:
        properties = deepcopy(tool.parameters['properties'])

        required = []
        for key, value in properties.items():
            if value["type"] == "any":
                value["type"] = "string"
            if not ("nullable" in value and value["nullable"]):
                required.append(key)

        model_id = model_id.split("/")[-1]

        if model_id in DEFAULT_ANTHROPIC_MODELS:
            return {
                "name": tool.name,
                "description": tool.description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        else:
            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }

    def get_clean_completion_kwargs(self, completion_kwargs: Dict[str, Any]):

        model_id = self.model_id.split("/")[-1]

        if model_id in UNSUPPORTED_TOOL_CHOICE_MODELS:
            completion_kwargs.pop("tool_choice", None)
        if model_id in UNSUPPORTED_STOP_MODELS:
            completion_kwargs.pop("stop", None)
        return completion_kwargs