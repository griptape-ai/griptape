from __future__ import annotations

from collections.abc import Iterator
from typing import Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    PromptStack,
    PromptStackMessage,
    DeltaPromptStackMessage,
    BaseDeltaPromptStackContent,
    TextPromptStackContent,
    DeltaTextPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer

from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_input: str | Callable[[], str] = field(default="mock input", kw_only=True)
    mock_output: str | Callable[[PromptStack], str] = field(default="mock output", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        return PromptStackMessage(
            content=[TextPromptStackContent(TextArtifact(output))],
            role=PromptStackMessage.ASSISTANT_ROLE,
            usage=PromptStackMessage.Usage(input_tokens=100, output_tokens=100),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        yield DeltaTextPromptStackContent(output)
        yield DeltaPromptStackMessage(
            delta_usage=DeltaPromptStackMessage.DeltaUsage(input_tokens=100, output_tokens=100)
        )
