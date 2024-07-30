from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field
from schema import Schema

from griptape.artifacts import (
    ActionArtifact,
    BaseArtifact,
    ErrorArtifact,
    ImageArtifact,
    InfoArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.common import (
    ActionCallDeltaMessageContent,
    ActionCallMessageContent,
    ActionResultMessageContent,
    BaseDeltaMessageContent,
    BaseMessageContent,
    DeltaMessage,
    ImageMessageContent,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
    observable,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from collections.abc import Iterator

    from anthropic import Client
    from anthropic.types import ContentBlock, ContentBlockDeltaEvent, ContentBlockStartEvent

    from griptape.tools.base_tool import BaseTool


@define
class AnthropicPromptDriver(BasePromptDriver):
    """Anthropic Prompt Driver.

    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
    """

    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key),
            takes_self=True,
        ),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})
    tool_choice: dict = field(default=Factory(lambda: {"type": "auto"}), kw_only=True, metadata={"serializable": False})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=1000, kw_only=True, metadata={"serializable": True})

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return Message(
            content=[self.__to_prompt_stack_message_content(content) for content in response.content],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        events = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for event in events:
            if event.type == "content_block_delta" or event.type == "content_block_start":
                yield DeltaMessage(content=self.__to_prompt_stack_delta_message_content(event))
            elif event.type == "message_start":
                yield DeltaMessage(usage=DeltaMessage.Usage(input_tokens=event.message.usage.input_tokens))
            elif event.type == "message_delta":
                yield DeltaMessage(usage=DeltaMessage.Usage(output_tokens=event.usage.output_tokens))

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self.__to_anthropic_messages([i for i in prompt_stack.messages if not i.is_system()])

        system_messages = prompt_stack.system_messages
        system_message = system_messages[0].to_text() if system_messages else None

        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            "messages": messages,
            **(
                {"tools": self.__to_anthropic_tools(prompt_stack.tools), "tool_choice": self.tool_choice}
                if prompt_stack.tools and self.use_native_tools
                else {}
            ),
            **({"system": system_message} if system_message else {}),
        }

    def __to_anthropic_messages(self, messages: list[Message]) -> list[dict]:
        return [
            {"role": self.__to_anthropic_role(message), "content": self.__to_anthropic_content(message)}
            for message in messages
        ]

    def __to_anthropic_role(self, message: Message) -> str:
        if message.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_anthropic_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "name": tool.to_native_tool_name(activity),
                "description": tool.activity_description(activity),
                "input_schema": (tool.activity_schema(activity) or Schema({})).json_schema("Input Schema"),
            }
            for tool in tools
            for activity in tool.activities()
        ]

    def __to_anthropic_content(self, message: Message) -> str | list[dict]:
        if message.has_all_content_type(TextMessageContent):
            return message.to_text()
        else:
            return [self.__to_anthropic_message_content(content) for content in message.content]

    def __to_anthropic_message_content(self, content: BaseMessageContent) -> dict:
        if isinstance(content, TextMessageContent):
            return {"type": "text", "text": content.artifact.value}
        elif isinstance(content, ImageMessageContent):
            artifact = content.artifact

            return {
                "type": "image",
                "source": {"type": "base64", "media_type": artifact.mime_type, "data": artifact.base64},
            }
        elif isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return {"type": "tool_use", "id": action.tag, "name": action.to_native_tool_name(), "input": action.input}
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            if isinstance(artifact, ListArtifact):
                message_content = [self.__to_anthropic_tool_result_content(artifact) for artifact in artifact.value]
            else:
                message_content = [self.__to_anthropic_tool_result_content(artifact)]

            return {
                "type": "tool_result",
                "tool_use_id": content.action.tag,
                "content": message_content,
                "is_error": isinstance(artifact, ErrorArtifact),
            }
        else:
            raise ValueError(f"Unsupported prompt content type: {type(content)}")

    def __to_anthropic_tool_result_content(self, artifact: BaseArtifact) -> dict:
        if isinstance(artifact, ImageArtifact):
            return {
                "type": "image",
                "source": {"type": "base64", "media_type": artifact.mime_type, "data": artifact.base64},
            }
        elif isinstance(artifact, (TextArtifact, ErrorArtifact, InfoArtifact)):
            return {"type": "text", "text": artifact.to_text()}
        else:
            raise ValueError(f"Unsupported tool result artifact type: {type(artifact)}")

    def __to_prompt_stack_message_content(self, content: ContentBlock) -> BaseMessageContent:
        if content.type == "text":
            return TextMessageContent(TextArtifact(content.text))
        elif content.type == "tool_use":
            name, path = ToolAction.from_native_tool_name(content.name)

            return ActionCallMessageContent(
                artifact=ActionArtifact(
                    value=ToolAction(tag=content.id, name=name, path=path, input=content.input),  # pyright: ignore[reportArgumentType]
                ),
            )
        else:
            raise ValueError(f"Unsupported message content type: {content.type}")

    def __to_prompt_stack_delta_message_content(
        self,
        event: ContentBlockDeltaEvent | ContentBlockStartEvent,
    ) -> BaseDeltaMessageContent:
        if event.type == "content_block_start":
            content_block = event.content_block

            if content_block.type == "tool_use":
                name, path = ToolAction.from_native_tool_name(content_block.name)

                return ActionCallDeltaMessageContent(index=event.index, tag=content_block.id, name=name, path=path)
            elif content_block.type == "text":
                return TextDeltaMessageContent(content_block.text, index=event.index)
            else:
                raise ValueError(f"Unsupported content block type: {content_block.type}")
        elif event.type == "content_block_delta":
            content_block_delta = event.delta

            if content_block_delta.type == "text_delta":
                return TextDeltaMessageContent(content_block_delta.text, index=event.index)
            elif content_block_delta.type == "input_json_delta":
                return ActionCallDeltaMessageContent(index=event.index, partial_input=content_block_delta.partial_json)
            else:
                raise ValueError(f"Unsupported message content type: {event}")
        else:
            raise ValueError(f"Unsupported message content type: {event}")
