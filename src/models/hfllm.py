import warnings
from typing import Dict, List, Optional, Any
from dataclasses import asdict, dataclass
import os
from collections.abc import Generator
from src.models.base import (ApiModel,
                             ChatMessage,
                             tool_role_conversions,
                             TokenUsage,
                             ChatMessageStreamDelta,
                             ChatMessageToolCallStreamDelta)
from src.models.message_manager import (
    MessageManager
)

STRUCTURED_GENERATION_PROVIDERS = ["cerebras", "fireworks-ai"]

class InferenceClientModel(ApiModel):
    """A class to interact with Hugging Face's Inference Providers for language model interaction."""

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct",
        provider: str | None = None,
        token: str | None = None,
        timeout: int = 120,
        client_kwargs: dict[str, Any] | None = None,
        custom_role_conversions: dict[str, str] | None = None,
        api_key: str | None = None,
        bill_to: str | None = None,
        base_url: str | None = None,
        http_client=None,
        **kwargs,
    ):
        if token is not None and api_key is not None:
            raise ValueError(
                "Received both `token` and `api_key` arguments. Please provide only one of them."
                " `api_key` is an alias for `token` to make the API compatible with OpenAI's client."
                " It has the exact same behavior as `token`."
            )

        self.http_client = http_client
        self.message_manager = MessageManager(model_id=model_id)

        token = token if token is not None else api_key
        if token is None:
            token = os.getenv("HUGGINEFACE_API_KEY")

        self.client_kwargs = {
            **(client_kwargs or {}),
            "model": model_id,
            "provider": provider,
            "token": token,
            "timeout": timeout,
            "bill_to": bill_to,
            "base_url": base_url,
        }
        super().__init__(model_id=model_id, custom_role_conversions=custom_role_conversions, **kwargs)

    def create_client(self):
        """Create the Hugging Face client."""
        from huggingface_hub import InferenceClient

        return InferenceClient(**self.client_kwargs)

    async def generate(
        self,
        messages: list[ChatMessage],
        stop_sequences: list[str] | None = None,
        response_format: dict[str, str] | None = None,
        tools_to_call_from: list[Any] | None = None,
        **kwargs,
    ) -> ChatMessage:
        if response_format is not None and self.client_kwargs["provider"] not in STRUCTURED_GENERATION_PROVIDERS:
            raise ValueError(
                "InferenceClientModel only supports structured outputs with these providers:"
                + ", ".join(STRUCTURED_GENERATION_PROVIDERS)
            )
        completion_kwargs = self._prepare_completion_kwargs(
            messages=messages,
            stop_sequences=stop_sequences,
            tools_to_call_from=tools_to_call_from,
            # response_format=response_format,
            convert_images_to_image_urls=True,
            http_client=self.http_client,
            custom_role_conversions=self.custom_role_conversions,
            **kwargs,
        )
        response = self.client.chat_completion(**completion_kwargs)

        self._last_input_token_count = response.usage.prompt_tokens
        self._last_output_token_count = response.usage.completion_tokens
        return ChatMessage.from_dict(
            asdict(response.choices[0].message),
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