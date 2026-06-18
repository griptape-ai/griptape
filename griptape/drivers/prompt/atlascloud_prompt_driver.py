from __future__ import annotations

import os

from attrs import Factory, define, field

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver


@define
class AtlasCloudPromptDriver(OpenAiChatPromptDriver):
    """Atlas Cloud Prompt Driver.

    Atlas Cloud is an OpenAI-compatible LLM provider that gives access to 300+ models
    (DeepSeek, Qwen, Claude, GPT, Gemini, and more) through a unified API.

    Attributes:
        base_url: The Atlas Cloud API base URL.
        api_key: An optional Atlas Cloud API key. If not provided, the `ATLASCLOUD_API_KEY`
            environment variable will be used.
        model: The model to use. Defaults to `deepseek-ai/deepseek-v4-pro`.

    For available models, see https://atlascloud.ai/docs/models.
    """

    base_url: str = field(
        default="https://api.atlascloud.ai/v1",
        kw_only=True,
        metadata={"serializable": True},
    )
    api_key: str | None = field(
        default=Factory(lambda: os.getenv("ATLASCLOUD_API_KEY")),
        kw_only=True,
        metadata={"serializable": False},
    )
    model: str = field(
        default="deepseek-ai/deepseek-v4-pro",
        kw_only=True,
        metadata={"serializable": True},
    )
