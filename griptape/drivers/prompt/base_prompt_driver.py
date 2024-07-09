from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.common import (
    BaseDeltaMessageContent,
    DeltaMessage,
    TextDeltaMessageContent,
    PromptStack,
    Message,
    TextMessageContent,
)
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.structures import Structure


@define(kw_only=True)
class BasePromptDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    """Base class for the Prompt Drivers.

    Attributes:
        temperature: The temperature to use for the completion.
        max_tokens: The maximum number of tokens to generate. If not specified, the value will be automatically generated based by the tokenizer.
        structure: An optional `Structure` to publish events to.
        prompt_stack_to_string: A function that converts a `PromptStack` to a string.
        ignored_exception_types: A tuple of exception types to ignore.
        model: The model name.
        tokenizer: An instance of `BaseTokenizer` to when calculating tokens.
        stream: Whether to stream the completion or not. `CompletionChunkEvent`s will be published to the `Structure` if one is provided.
    """

    temperature: float = field(default=0.1, metadata={"serializable": True})
    max_tokens: Optional[int] = field(default=None, metadata={"serializable": True})
    structure: Optional[Structure] = field(default=None)
    ignored_exception_types: tuple[type[Exception], ...] = field(default=Factory(lambda: (ImportError, ValueError)))
    model: str = field(metadata={"serializable": True})
    tokenizer: BaseTokenizer
    stream: bool = field(default=False, metadata={"serializable": True})

    def before_run(self, prompt_stack: PromptStack) -> None:
        if self.structure:
            self.structure.publish_event(StartPromptEvent(model=self.model, prompt_stack=prompt_stack))

    def after_run(self, result: Message) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(
                    model=self.model,
                    result=result.value,
                    input_token_count=result.usage.input_tokens,
                    output_token_count=result.usage.output_tokens,
                )
            )

    def run(self, prompt_stack: PromptStack) -> Message:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                result = self.__process_stream(prompt_stack) if self.stream else self.__process_run(prompt_stack)

                self.after_run(result)

                return result
        else:
            raise Exception("prompt driver failed after all retry attempts")

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        """Converts a Prompt Stack to a string for token counting or model input.
        This base implementation is only a rough approximation, and should be overridden by subclasses with model-specific tokens.

        Args:
            prompt_stack: The Prompt Stack to convert to a string.

        Returns:
            A single string representation of the Prompt Stack.
        """
        prompt_lines = []

        for i in prompt_stack.messages:
            content = i.to_text()
            if i.is_user():
                prompt_lines.append(f"User: {content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {content}")
            else:
                prompt_lines.append(content)

        prompt_lines.append("Assistant:")

        return "\n\n".join(prompt_lines)

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> Message: ...

    @abstractmethod
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]: ...

    def __process_run(self, prompt_stack: PromptStack) -> Message:
        result = self.try_run(prompt_stack)

        return result

    def __process_stream(self, prompt_stack: PromptStack) -> Message:
        delta_contents: dict[int, list[BaseDeltaMessageContent]] = {}
        usage = DeltaMessage.Usage()

        # Aggregate all content deltas from the stream
        deltas = self.try_stream(prompt_stack)
        for delta in deltas:
            usage += delta.usage

            if delta.content is not None:
                if delta.content.index in delta_contents:
                    delta_contents[delta.content.index].append(delta.content)
                else:
                    delta_contents[delta.content.index] = [delta.content]

            if isinstance(delta.content, TextDeltaMessageContent):
                self.structure.publish_event(CompletionChunkEvent(token=delta.content.text))

        # Build a complete content from the content deltas
        content = []
        for deltas in delta_contents.values():
            text_deltas = [delta for delta in deltas if isinstance(delta, TextDeltaMessageContent)]
            if text_deltas:
                content.append(TextMessageContent.from_deltas(text_deltas))

        result = Message(
            content=content,
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

        return result
