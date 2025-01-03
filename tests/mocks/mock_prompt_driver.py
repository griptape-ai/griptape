from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable, Union

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.artifacts.action_artifact import ActionArtifact
from griptape.common import (
    ActionCallDeltaMessageContent,
    ActionCallMessageContent,
    DeltaMessage,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
)
from griptape.drivers import BasePromptDriver
from tests.mocks.mock_tokenizer import MockTokenizer

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.tokenizers import BaseTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_input: Union[str, Callable[[], str]] = field(default="mock input", kw_only=True)
    mock_output: Union[str, Callable[[PromptStack], str]] = field(default="mock output", kw_only=True)
    mock_structured_output: Union[dict, Callable[[PromptStack], dict]] = field(factory=dict, kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> Message:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        if self.use_native_tools and prompt_stack.tools:
            # Hack to simulate CoT. If there are any action messages in the prompt stack, give the answer.
            action_messages = [
                message for message in prompt_stack.messages if message.has_any_content_type(ActionCallMessageContent)
            ]
            if any(action_messages):
                return Message(
                    content=[TextMessageContent(TextArtifact(f"Answer: {output}"))],
                    role=Message.ASSISTANT_ROLE,
                    usage=Message.Usage(input_tokens=100, output_tokens=100),
                )
            else:
                if self.structured_output_strategy == "tool":
                    tool_action = ToolAction(
                        tag="mock-tag",
                        name="StructuredOutputTool",
                        path="provide_output",
                        input={"values": self.mock_structured_output},
                    )
                else:
                    tool_action = ToolAction(
                        tag="mock-tag",
                        name="MockTool",
                        path="test",
                        input={"values": {"test": "test-value"}},
                    )

                return Message(
                    content=[ActionCallMessageContent(ActionArtifact(tool_action))],
                    role=Message.ASSISTANT_ROLE,
                    usage=Message.Usage(input_tokens=100, output_tokens=100),
                )
        else:
            if prompt_stack.output_schema is not None:
                return Message(
                    content=[TextMessageContent(TextArtifact(json.dumps(self.mock_structured_output)))],
                    role=Message.ASSISTANT_ROLE,
                    usage=Message.Usage(input_tokens=100, output_tokens=100),
                )
            else:
                return Message(
                    content=[TextMessageContent(TextArtifact(output))],
                    role=Message.ASSISTANT_ROLE,
                    usage=Message.Usage(input_tokens=100, output_tokens=100),
                )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        output = self.mock_output(prompt_stack) if isinstance(self.mock_output, Callable) else self.mock_output

        if self.use_native_tools and prompt_stack.tools:
            # Hack to simulate CoT. If there are any action messages in the prompt stack, give the answer.
            action_messages = [
                message for message in prompt_stack.messages if message.has_any_content_type(ActionCallMessageContent)
            ]
            if any(action_messages):
                yield DeltaMessage(content=TextDeltaMessageContent(f"Answer: {output}"))
                yield DeltaMessage(usage=DeltaMessage.Usage(input_tokens=100, output_tokens=100))
            else:
                if self.structured_output_strategy == "tool":
                    yield DeltaMessage(
                        content=ActionCallDeltaMessageContent(
                            tag="mock-tag",
                            name="StructuredOutputTool",
                            path="provide_output",
                        )
                    )
                    yield DeltaMessage(
                        content=ActionCallDeltaMessageContent(
                            partial_input=json.dumps({"values": self.mock_structured_output})
                        )
                    )
                else:
                    yield DeltaMessage(
                        content=ActionCallDeltaMessageContent(
                            tag="mock-tag",
                            name="MockTool",
                            path="test",
                        )
                    )
                    yield DeltaMessage(
                        content=ActionCallDeltaMessageContent(partial_input='{ "values": { "test": "test-value" } }')
                    )
        else:
            if prompt_stack.output_schema is not None:
                yield DeltaMessage(
                    content=TextDeltaMessageContent(json.dumps(self.mock_structured_output)),
                    role=Message.ASSISTANT_ROLE,
                    usage=Message.Usage(input_tokens=100, output_tokens=100),
                )
            else:
                yield DeltaMessage(content=TextDeltaMessageContent(output))
