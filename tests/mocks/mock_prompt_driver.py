from __future__ import annotations

from collections.abc import Iterator
from typing import Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import MessageStack, Message, DeltaMessage, TextMessageContent, TextDeltaMessageContent
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer

from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_input: str | Callable[[], str] = field(default="mock input", kw_only=True)
    mock_output: str | Callable[[MessageStack], str] = field(default="mock output", kw_only=True)

    def try_run(self, message_stack: MessageStack) -> Message:
        output = self.mock_output(message_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        return Message(
            content=[TextMessageContent(TextArtifact(output))],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=100, output_tokens=100),
        )

    def try_stream(self, message_stack: MessageStack) -> Iterator[DeltaMessage]:
        output = self.mock_output(message_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        yield DeltaMessage(content=TextDeltaMessageContent(output))

        yield DeltaMessage(usage=DeltaMessage.Usage(input_tokens=100, output_tokens=100))
