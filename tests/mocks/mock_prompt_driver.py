from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import DeltaMessage, Message, PromptStack, TextDeltaMessageContent, TextMessageContent
from griptape.drivers import BasePromptDriver
from tests.mocks.mock_tokenizer import MockTokenizer

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.tokenizers import BaseTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_input: str | Callable[[], str] = field(default="mock input", kw_only=True)
    mock_output: str | Callable[[PromptStack], str] = field(default="mock output", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> Message:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        return Message(
            content=[TextMessageContent(TextArtifact(output))],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=100, output_tokens=100),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        yield DeltaMessage(content=TextDeltaMessageContent(output))

        yield DeltaMessage(usage=DeltaMessage.Usage(input_tokens=100, output_tokens=100))
