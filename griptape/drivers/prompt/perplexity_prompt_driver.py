from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from typing_extensions import override

from griptape.common import PromptStack
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import ChatCompletion

    from griptape.common import PromptStack
    from griptape.common.prompt_stack.messages.message import Message


@define
class PerplexityPromptDriver(OpenAiChatPromptDriver):
    base_url: str = field(default="https://api.perplexity.ai", kw_only=True, metadata={"serializable": True})
    structured_output_strategy: str = field(default="native", kw_only=True, metadata={"serializable": True})

    @override
    def _to_message(self, result: ChatCompletion) -> Message:
        message = super()._to_message(result)

        message.content[0].artifact.meta["citations"] = getattr(result, "citations", [])

        return message

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = super()._base_params(prompt_stack)

        if "stop" in params:
            del params["stop"]

        return params
