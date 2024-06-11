from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    DeltaPromptStackElement,
    DeltaTextPromptStackContent,
    PromptStack,
    PromptStackElement,
    TextPromptStackContent,
)
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.mixins import ExponentialBackoffMixin
from griptape.mixins.serializable_mixin import SerializableMixin
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
            self.structure.publish_event(
                StartPromptEvent(
                    model=self.model,
                    token_count=self.tokenizer.count_tokens(self.prompt_stack_to_string(prompt_stack)),
                    prompt_stack=prompt_stack,
                    prompt=self.prompt_stack_to_string(prompt_stack),
                )
            )

    def after_run(self, result: PromptStackElement) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(model=self.model, result=result.value, token_count=result.usage.output_tokens)
            )

    def run(self, prompt_stack: PromptStack) -> PromptStackElement:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                if self.stream:
                    tokens = []
                    delta_usage = DeltaPromptStackElement.DeltaUsage()

                    delta_elements = self.try_stream(prompt_stack)

                    for delta_element in delta_elements:
                        if isinstance(delta_element, DeltaPromptStackElement):
                            delta_usage += delta_element.delta_usage
                        elif isinstance(delta_element, DeltaTextPromptStackContent):
                            chunk_value = delta_element.artifact.value
                            self.structure.publish_event(CompletionChunkEvent(token=chunk_value))
                            tokens.append(chunk_value)

                    content = TextPromptStackContent(artifact=TextArtifact("".join(tokens).strip()))
                    result = PromptStackElement(
                        content=[content],
                        role=PromptStackElement.ASSISTANT_ROLE,
                        usage=PromptStackElement.Usage(
                            input_tokens=delta_usage.input_tokens or 0, output_tokens=delta_usage.output_tokens or 0
                        ),
                    )
                else:
                    result = self.try_run(prompt_stack)

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

        for i in prompt_stack.inputs:
            if i.is_user():
                prompt_lines.append(f"User: {i.content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(str(i.content))

        prompt_lines.append("Assistant:")

        return "\n\n".join(prompt_lines)

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement: ...

    @abstractmethod
    def try_stream(
        self, prompt_stack: PromptStack
    ) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]: ...
