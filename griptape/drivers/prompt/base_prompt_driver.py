from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.events import StartPromptEvent, FinishPromptEvent, CompletionChunkEvent
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils import PromptStack
from griptape.mixins import ExponentialBackoffMixin
from griptape.tokenizers import BaseTokenizer
from griptape.artifacts import TextArtifact

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
            self.structure.publish_event(
                StartPromptEvent(
                    model=self.model,
                    token_count=self.tokenizer.count_tokens(self.prompt_stack_to_string(prompt_stack)),
                    prompt_stack=prompt_stack,
                    prompt=self.prompt_stack_to_string(prompt_stack),
                )
            )

    def after_run(self, result: TextArtifact) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(
                    model=self.model, result=result.value, token_count=self.tokenizer.count_tokens(result.value)
                )
            )

    def run(self, prompt_stack: PromptStack) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                if self.stream:
                    tokens = []
                    completion_chunks = self.try_stream(prompt_stack)
                    for chunk in completion_chunks:
                        self.structure.publish_event(CompletionChunkEvent(token=chunk.value))
                        tokens.append(chunk.value)
                    result = TextArtifact(value="".join(tokens).strip())
                else:
                    result = self.try_run(prompt_stack)
                    result.value = result.value.strip()

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
                prompt_lines.append(i.content)

        prompt_lines.append("Assistant:")

        return "\n\n".join(prompt_lines)

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> TextArtifact: ...

    @abstractmethod
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]: ...
