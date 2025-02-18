from __future__ import annotations

from attrs import Factory, define, field

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.tokenizers.grok_tokenizer import GrokTokenizer


@define
class GrokPromptDriver(OpenAiChatPromptDriver):
    base_url: str = field(default="https://api.x.ai/v1", kw_only=True, metadata={"serializable": True})
    tokenizer: GrokTokenizer = field(
        default=Factory(
            lambda self: GrokTokenizer(base_url=self.base_url, api_key=self.api_key, model=self.model), takes_self=True
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
