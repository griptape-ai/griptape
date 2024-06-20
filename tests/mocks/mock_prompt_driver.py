from __future__ import annotations
from collections.abc import Iterator
from typing import Callable
from attrs import define, field
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer
from griptape.artifacts import TextArtifact
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_input: str | Callable[[], str] = field(default="mock input", kw_only=True)
    mock_output: str | Callable[[PromptStack], str] = field(default="mock output", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        return TextArtifact(
            value=self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        yield TextArtifact(
            value=self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output
        )
