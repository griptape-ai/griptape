from __future__ import annotations
from collections.abc import Iterator
from attrs import define

from griptape.artifacts import TextArtifact
from griptape.common import (
    PromptStack,
    PromptStackElement,
    TextPromptStackContent,
    DeltaPromptStackElement,
    DeltaTextPromptStackContent,
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

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            return PromptStackElement(
                content=[TextPromptStackContent(TextArtifact("success"))],
                role=PromptStackElement.ASSISTANT_ROLE,
                usage=PromptStackElement.Usage(input_tokens=100, output_tokens=100),
            )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            yield DeltaPromptStackElement(
                delta_content=DeltaTextPromptStackContent("success"),
                delta_usage=DeltaPromptStackElement.DeltaUsage(input_tokens=100, output_tokens=100),
            )
