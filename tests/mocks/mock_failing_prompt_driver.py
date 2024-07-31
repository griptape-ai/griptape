from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.common import DeltaMessage, Message, PromptStack


@define
class MockFailingPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

    def run(self, prompt_stack: PromptStack) -> Message:
        raise Exception("failed attempt")

    def stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        raise Exception("failed attempt")
