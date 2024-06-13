from __future__ import annotations

from collections.abc import Iterator
from typing import Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    PromptStack,
    PromptStackElement,
    DeltaPromptStackElement,
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

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        output = self.mock_output() if isinstance(self.mock_output, Callable) else self.mock_output

        return PromptStackElement(
            content=[TextPromptStackContent(TextArtifact(output))],
            role=PromptStackElement.ASSISTANT_ROLE,
            usage=PromptStackElement.Usage(input_tokens=100, output_tokens=100),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        output = self.mock_output() if isinstance(self.mock_output, Callable) else self.mock_output

        yield DeltaTextPromptStackContent(output)
        yield DeltaPromptStackElement(
            delta_usage=DeltaPromptStackElement.DeltaUsage(input_tokens=100, output_tokens=100)
        )
