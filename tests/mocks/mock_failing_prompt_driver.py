from __future__ import annotations
from collections.abc import Iterator
from attrs import define

from griptape.artifacts import TextArtifact
from griptape.common import (
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
    DeltaPromptStackMessage,
    TextDeltaPromptStackContent,
    BaseDeltaPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


@define
class MockFailingPromptDriver(BasePromptDriver):
    max_failures: int
    current_attempt: int = 0
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            return PromptStackMessage(
                content=[TextPromptStackContent(TextArtifact("success"))],
                role=PromptStackMessage.ASSISTANT_ROLE,
                usage=PromptStackMessage.Usage(input_tokens=100, output_tokens=100),
            )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            yield DeltaPromptStackMessage(
                delta_content=TextDeltaPromptStackContent("success"),
                usage=DeltaPromptStackMessage.Usage(input_tokens=100, output_tokens=100),
            )
