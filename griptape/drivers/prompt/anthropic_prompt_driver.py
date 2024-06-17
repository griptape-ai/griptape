from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.artifacts import ActionCallArtifact, ErrorArtifact, TextArtifact
from griptape.artifacts.base_artifact import BaseArtifact
from griptape.artifacts.image_artifact import ImageArtifact
from griptape.artifacts.info_artifact import InfoArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    BasePromptStackContent,
    DeltaPromptStackMessage,
    DeltaTextPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
)
from griptape.common import ActionCallPromptStackContent
from griptape.common import ActionResultPromptStackContent
from griptape.common import DeltaActionCallPromptStackContent
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency
from schema import Schema

if TYPE_CHECKING:
    from anthropic import Client
    from anthropic.types import ContentBlock, ContentBlockDeltaEvent, ContentBlockStartEvent
    from griptape.tools.base_tool import BaseTool


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
    """

    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})
    tool_choice: dict = field(default=Factory(lambda: {"type": "auto"}), kw_only=True, metadata={"serializable": False})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=1000, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return PromptStackMessage(
            content=[self.__message_content_to_prompt_stack_content(content) for content in response.content],
            role=response.role,
            usage=PromptStackMessage.Usage(
                input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        events = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for event in events:
            if event.type == "content_block_delta" or event.type == "content_block_start":
                yield self.__message_content_delta_to_prompt_stack_content_delta(event)
            elif event.type == "message_start":
                yield DeltaPromptStackMessage(
                    role=event.message.role,
                    delta_usage=DeltaPromptStackMessage.DeltaUsage(input_tokens=event.message.usage.input_tokens),
                )
            elif event.type == "message_delta":
                yield DeltaPromptStackMessage(
                    delta_usage=DeltaPromptStackMessage.DeltaUsage(output_tokens=event.usage.output_tokens)
                )

    def _prompt_stack_messages_to_messages(self, elements: list[PromptStackMessage]) -> list[dict]:
        return [{"role": self.__to_role(input), "content": self.__to_content(input)} for input in elements]

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"tools": self.__to_tools(prompt_stack.actions), "tool_choice": self.tool_choice}
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self._prompt_stack_messages_to_messages([i for i in prompt_stack.messages if not i.is_system()])

        system_element = next((i for i in prompt_stack.messages if i.is_system()), None)
        if system_element:
            system_message = system_element.to_text_artifact().to_text()
        else:
            system_message = None

        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            "messages": messages,
            **self._prompt_stack_to_tools(prompt_stack),
            **({"system": system_message} if system_message else {}),
        }

    def __to_role(self, input: PromptStackMessage) -> str:
        if input.is_system():
            return "system"
        elif input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "name": f"{tool.name}-{tool.activity_name(activity)}",
                "description": tool.activity_description(activity),
                "input_schema": (tool.activity_schema(activity) or Schema({})).json_schema("Input Schema"),
            }
            for tool in tools
            for activity in tool.activities()
        ]

    def __to_content(self, input: PromptStackElement) -> str | list[dict]:
        if all(isinstance(content, TextPromptStackContent) for content in input.content):
            return input.to_text_artifact().to_text()
        else:
            content = [self.__prompt_stack_content_to_message_content(content) for content in input.content]
            sorted_content = sorted(
                content, key=lambda message_content: -1 if message_content["type"] == "tool_result" else 1
            )  # Tool results must come first in the content list
            return sorted_content

    def __prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ImagePromptStackContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ActionCallPromptStackContent):
            action = content.artifact.value

            return {
                "type": "tool_use",
                "id": action.tag,
                "name": f"{action.name}-{action.path}",
                "input": json.loads(action.input),
            }
        elif isinstance(content, ActionResultPromptStackContent):
            artifact = content.artifact

            return {
                "type": "tool_result",
                "tool_use_id": content.action_tag,
                "content": [self.__artifact_to_message_content(artifact) for artifact in artifact.value]
                if isinstance(artifact, ListArtifact)
                else [self.__artifact_to_message_content(artifact)],
                "is_error": isinstance(artifact, ErrorArtifact),
            }
        else:
            raise ValueError(f"Unsupported prompt content type: {type(content)}")

    def __artifact_to_message_content(self, artifact: BaseArtifact) -> dict:
        if isinstance(artifact, ImageArtifact):
            return {
                "type": "image",
                "source": {"type": "base64", "media_type": artifact.mime_type, "data": artifact.base64},
            }
        elif (
            isinstance(artifact, TextArtifact)
            or isinstance(artifact, ErrorArtifact)
            or isinstance(artifact, InfoArtifact)
        ):
            return {"text": artifact.to_text()}
        elif isinstance(artifact, ErrorArtifact):
            return {"text": artifact.to_text()}
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")

    def __message_content_to_prompt_stack_content(self, content: ContentBlock) -> BasePromptStackContent:
        if content.type == "text":
            return TextPromptStackContent(TextArtifact(content.text))
        elif content.type == "tool_use":
            return ActionCallPromptStackContent(
                artifact=ActionCallArtifact(
                    value=ActionCallArtifact.ActionCall(
                        tag=content.id,
                        name=content.name.split("-")[0],
                        path=content.name.split("-")[1],
                        input=json.dumps(content.input),
                    )
                )
            )
        else:
            raise ValueError(f"Unsupported message content type: {content.type}")

    def __message_content_delta_to_prompt_stack_content_delta(
        self, event: ContentBlockDeltaEvent | ContentBlockStartEvent
    ) -> BaseDeltaPromptStackContent:
        index = content_delta.index

        if content_delta.delta.type == "text_delta":
            return DeltaTextPromptStackContent(content_delta.delta.text, index=index)
        else:
            raise ValueError(f"Unsupported message content delta type : {content_delta.delta.type}")
