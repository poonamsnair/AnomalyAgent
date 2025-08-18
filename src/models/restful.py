import json
from typing import Dict, List, Optional, Any
from collections.abc import Generator
from openai.types.chat import ChatCompletion
import requests
import os
from PIL import Image

from src.models.base import (ApiModel,
                             Model,
                             ChatMessage,
                             tool_role_conversions,
                             ChatMessageStreamDelta,
                             ChatMessageToolCallStreamDelta)
from src.models.message_manager import MessageManager
from src.logger import TokenUsage, logger
from src.utils import encode_image_base64


class RestfulClient():
    def __init__(self,
                 api_base: str,
                 api_key: str,
                 api_type: str = "chat/completions",
                 model_id: str = "o3",
                 http_client=None):
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.model_id = model_id
        self.http_client = http_client

    def completion(self, model, messages, **kwargs):
        headers = {
            "app_key": self.api_key,
            "Content-Type": "application/json"
        }

        model = model.split("/")[-1]
        data = {
            "model": model,
            "messages": messages,
        }

        # Add any additional kwargs to the data
        if kwargs:
            data.update(kwargs)

        response = requests.post(
            f"{self.api_base}/{self.api_type}",
            json=data,
            headers=headers,
        )

        return response.json()


class RestfulModel(ApiModel):
    """This model connects to an OpenAI-compatible API server."""

    def __init__(
        self,
        model_id: str,
        api_base: Optional[str] = None,
        api_type: str = "chat/completions",
        api_key: Optional[str] = None,
        custom_role_conversions: dict[str, str] | None = None,
        flatten_messages_as_text: bool = False,
        http_client=None,
        **kwargs,
    ):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        flatten_messages_as_text = (
            flatten_messages_as_text
            if flatten_messages_as_text is not None
            else model_id.startswith(("ollama", "groq", "cerebras"))
        )

        self.http_client = http_client
        self.message_manager = MessageManager(model_id=model_id)

        super().__init__(
            model_id=model_id,
            custom_role_conversions=custom_role_conversions,
            flatten_messages_as_text=flatten_messages_as_text,
            **kwargs,
        )

    def create_client(self):
        return RestfulClient(api_base=self.api_base,
                             api_key=self.api_key,
                             api_type=self.api_type,
                             model_id=self.model_id,
                             http_client=self.http_client)

    async def generate(
        self,
        messages: list[ChatMessage],
        stop_sequences: list[str] | None = None,
        response_format: dict[str, str] | None = None,
        tools_to_call_from: list[Any] | None = None,
        **kwargs,
    ) -> ChatMessage:

        completion_kwargs = self._prepare_completion_kwargs(
            messages=messages,
            stop_sequences=stop_sequences,
            response_format=response_format,
            tools_to_call_from=tools_to_call_from,
            model=self.model_id,
            convert_images_to_image_urls=True,
            custom_role_conversions=self.custom_role_conversions,
            **kwargs,
        )

        # Async call to the LiteLLM client for completion
        response = self.client.completion(**completion_kwargs)

        response = ChatCompletion.model_validate(response)

        self._last_input_token_count = response.usage.prompt_tokens
        self._last_output_token_count = response.usage.completion_tokens
        return ChatMessage.from_dict(
            response.choices[0].message.model_dump(include={"role", "content", "tool_calls"}),
            raw=response,
            token_usage=TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            ),
        )

    async def __call__(self, *args, **kwargs) -> ChatMessage:
        """
        Call the model with the given arguments.
        This is a convenience method that calls `generate` with the same arguments.
        """
        return await self.generate(*args, **kwargs)


# Simplified versions of other restful models
class RestfulTranscribeModel(ApiModel):
    def __init__(self, model_id: str, api_base: Optional[str] = None, api_key: Optional[str] = None, api_type: str = "wisper", http_client=None, **kwargs):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.http_client = http_client
        super().__init__(model_id=model_id, **kwargs)

    def create_client(self):
        return RestfulClient(api_base=self.api_base, api_key=self.api_key, api_type=self.api_type, model_id=self.model_id, http_client=self.http_client)


class RestfulImagenModel(ApiModel):
    def __init__(self, model_id: str, api_base: Optional[str] = None, api_key: Optional[str] = None, api_type: str = "imagen", http_client=None, **kwargs):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.http_client = http_client
        super().__init__(model_id=model_id, **kwargs)

    def create_client(self):
        return RestfulClient(api_base=self.api_base, api_key=self.api_key, api_type=self.api_type, model_id=self.model_id, http_client=self.http_client)


class RestfulVeoPridictModel(ApiModel):
    def __init__(self, model_id: str, api_base: Optional[str] = None, api_key: Optional[str] = None, api_type: str = "veo/predict", http_client=None, **kwargs):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.http_client = http_client
        super().__init__(model_id=model_id, **kwargs)

    def create_client(self):
        return RestfulClient(api_base=self.api_base, api_key=self.api_key, api_type=self.api_type, model_id=self.model_id, http_client=self.http_client)


class RestfulVeoFetchModel(ApiModel):
    def __init__(self, model_id: str, api_base: Optional[str] = None, api_key: Optional[str] = None, api_type: str = "veo/fetch", http_client=None, **kwargs):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.http_client = http_client
        super().__init__(model_id=model_id, **kwargs)

    def create_client(self):
        return RestfulClient(api_base=self.api_base, api_key=self.api_key, api_type=self.api_type, model_id=self.model_id, http_client=self.http_client)


class RestfulResponseModel(ApiModel):
    def __init__(self, model_id: str, api_base: Optional[str] = None, api_type: str = "responses", api_key: Optional[str] = None, custom_role_conversions: dict[str, str] | None = None, flatten_messages_as_text: bool = False, http_client=None, **kwargs):
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.api_type = api_type
        self.http_client = http_client
        self.message_manager = MessageManager(model_id=model_id)
        super().__init__(model_id=model_id, custom_role_conversions=custom_role_conversions, flatten_messages_as_text=flatten_messages_as_text, **kwargs)

    def create_client(self):
        return RestfulClient(api_base=self.api_base, api_key=self.api_key, api_type=self.api_type, model_id=self.model_id, http_client=self.http_client)