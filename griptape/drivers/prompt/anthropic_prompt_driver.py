from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    BasePromptStackContent,
    DeltaPromptStackElement,
    DeltaTextPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackElement,
    TextPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency


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

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return PromptStackElement(
            content=[TextPromptStackContent(TextArtifact(content)) for content in response.content],
            role=response.role,
            usage=PromptStackElement.Usage(
                input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        events = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for event in events:
            if event.type == "content_block_delta":
                yield DeltaTextPromptStackContent(TextArtifact(value=event.delta.text), index=event.index)
            elif event.type == "message_start":
                yield DeltaPromptStackElement(
                    role=event.message.role,
                    delta_usage=DeltaPromptStackElement.DeltaUsage(input_tokens=event.message.usage.input_tokens),
                )
            elif event.type == "message_delta":
                yield DeltaPromptStackElement(
                    delta_usage=DeltaPromptStackElement.DeltaUsage(output_tokens=event.usage.output_tokens)
                )

    def _prompt_stack_elements_to_messages(self, elements: list[PromptStackElement]) -> list[dict]:
        return [
            {"role": self.__to_role(input), "text": [self.__to_content(content) for content in input.content]}
            for input in elements
        ]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self._prompt_stack_elements_to_messages([i for i in prompt_stack.inputs if not i.is_system()])

        system_element = next((i for i in prompt_stack.inputs if i.is_system()), None)

        system_message = None
        if len(system_element.content) == 1:
            system_message = system_element.content[0].artifact.to_text()
        else:
            raise ValueError("System element must have exactly one content.")

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

    def __to_role(self, input: PromptStackElement) -> str:
        if input.is_system():
            return "system"
        elif input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": content.artifact.media_type,
                    "data": content.artifact.base64,
                },
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
