from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    DeltaPromptStackMessage,
    TextDeltaPromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
)
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BasePromptDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    """Base class for Prompt Drivers.

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

    temperature: float = field(default=0.1, kw_only=True, metadata={"serializable": True})
    max_tokens: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    structure: Optional[Structure] = field(default=None, kw_only=True)
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(lambda: (ImportError, ValueError)), kw_only=True
    )
    model: str = field(metadata={"serializable": True})
    tokenizer: BaseTokenizer
    stream: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    def before_run(self, prompt_stack: PromptStack) -> None:
        if self.structure:
            self.structure.publish_event(StartPromptEvent(model=self.model, prompt_stack=prompt_stack))

    def after_run(self, result: PromptStackMessage) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(
                    model=self.model,
                    result=result.value,
                    input_token_count=result.usage.input_tokens,
                    output_token_count=result.usage.output_tokens,
                )
            )

    def run(self, prompt_stack: PromptStack) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                if self.stream:
                    result = self.__process_stream(prompt_stack)
                else:
                    result = self.__process_run(prompt_stack)

                self.after_run(result)

                return result.to_text_artifact()
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
            content = i.to_text_artifact().to_text()
            if i.is_user():
                prompt_lines.append(f"User: {content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {content}")
            else:
                prompt_lines.append(content)

        prompt_lines.append("Assistant:")

        return "\n\n".join(prompt_lines)

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage: ...

    @abstractmethod
    def try_stream(
        self, prompt_stack: PromptStack
    ) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]: ...

    def __process_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        result = self.try_run(prompt_stack)

        return result

    def __process_stream(self, prompt_stack: PromptStack) -> PromptStackMessage:
        delta_contents: dict[int, list[BaseDeltaPromptStackContent]] = {}
        usage = DeltaPromptStackMessage.Usage()

        deltas = self.try_stream(prompt_stack)

        for delta in deltas:
            if isinstance(delta, DeltaPromptStackMessage):
                usage += delta.usage
            elif isinstance(delta, BaseDeltaPromptStackContent):
                if delta.index in delta_contents:
                    delta_contents[delta.index].append(delta)
                else:
                    delta_contents[delta.index] = [delta]

                if isinstance(delta, TextDeltaPromptStackContent):
                    self.structure.publish_event(CompletionChunkEvent(token=delta.text))

        content = []
        for index, deltas in delta_contents.items():
            text_deltas = [delta for delta in deltas if isinstance(delta, TextDeltaPromptStackContent)]
            if text_deltas:
                content.append(TextPromptStackContent.from_deltas(text_deltas))

        result = PromptStackMessage(
            content=content,
            role=PromptStackMessage.ASSISTANT_ROLE,
            usage=PromptStackMessage.Usage(
                input_tokens=usage.input_tokens or 0, output_tokens=usage.output_tokens or 0
            ),
        )

        return result
