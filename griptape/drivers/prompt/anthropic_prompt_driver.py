from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Optional, TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BasePromptStackContent,
    DeltaPromptStackMessage,
    TextDeltaPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from anthropic.types import ContentBlockDeltaEvent
    from anthropic.types import ContentBlock


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
    client: Any = field(
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
    max_tokens: int = field(default=1000, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return PromptStackMessage(
            content=[self.__message_content_to_prompt_stack_content(content) for content in response.content],
            role=PromptStackMessage.ASSISTANT_ROLE,
            usage=PromptStackMessage.Usage(
                input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage]:
        events = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for event in events:
            if event.type == "content_block_delta":
                yield DeltaPromptStackMessage(content=self.__message_content_delta_to_prompt_stack_content_delta(event))
            elif event.type == "message_start":
                yield DeltaPromptStackMessage(
                    usage=DeltaPromptStackMessage.Usage(input_tokens=event.message.usage.input_tokens)
                )
            elif event.type == "message_delta":
                yield DeltaPromptStackMessage(
                    usage=DeltaPromptStackMessage.Usage(output_tokens=event.usage.output_tokens)
                )

    def _prompt_stack_messages_to_messages(self, elements: list[PromptStackMessage]) -> list[dict]:
        return [{"role": self.__to_role(input), "content": self.__to_content(input)} for input in elements]

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
            **({"system": system_message} if system_message else {}),
        }

    def __to_role(self, input: PromptStackMessage) -> str:
        if input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_content(self, input: PromptStackMessage) -> str | list[dict]:
        if all(isinstance(content, TextPromptStackContent) for content in input.content):
            return input.to_text_artifact().to_text()
        else:
            return [self.__prompt_stack_content_message_content(content) for content in input.content]

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "type": "image",
                "source": {"type": "base64", "media_type": content.artifact.mime_type, "data": content.artifact.base64},
            }
        else:
            raise ValueError(f"Unsupported prompt content type: {type(content)}")

    def __message_content_to_prompt_stack_content(self, content: ContentBlock) -> BasePromptStackContent:
        if content.type == "text":
            return TextPromptStackContent(TextArtifact(content.text))
        else:
            raise ValueError(f"Unsupported message content type: {content.type}")

    def __message_content_delta_to_prompt_stack_content_delta(
        self, content_delta: ContentBlockDeltaEvent
    ) -> TextDeltaPromptStackContent:
        index = content_delta.index

        if content_delta.delta.type == "text_delta":
            return TextDeltaPromptStackContent(content_delta.delta.text, index=index)
        else:
            raise ValueError(f"Unsupported message content delta type : {content_delta.delta.type}")
