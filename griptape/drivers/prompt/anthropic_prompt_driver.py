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
            content=[self.message_content_to_prompt_stack_content(content) for content in response.content],
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

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        message_content = [self.prompt_stack_content_to_message_content(content) for content in prompt_input.content]

        if prompt_input.is_system():
            return {"role": "system", "content": message_content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": message_content}
        else:
            return {"role": "user", "content": message_content}

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
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

    def message_content_to_prompt_stack_content(self, message_content: dict) -> BasePromptStackContent:
        if message_content["type"] == "text":
            return TextPromptStackContent(TextArtifact(message_content["text"]))
        else:
            raise ValueError(f"Unsupported message content type: {message_content['type']}")

    def _prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        content = prompt_input.content

        if prompt_input.is_system():
            return {"role": "system", "content": content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        messages = [
            self.prompt_stack_input_to_message(prompt_input)
            for prompt_input in prompt_stack.inputs
            if not prompt_input.is_system()
        ]
        system = next((self.prompt_stack_input_to_message(i) for i in prompt_stack.inputs if i.is_system()), None)

        if system is None:
            return {"messages": messages}
        else:
            return {"messages": messages, "system": system["content"]}

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            **self._prompt_stack_to_model_input(prompt_stack),
        }
