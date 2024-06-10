from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from collections.abc import Iterator

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import PartialPromptStackElement, PromptStack, PromptStackElement
from griptape.common import TextDeltaPromptStackContent
from griptape.common.prompt_stack.contents.text_prompt_stack_content import TextPromptStackContent
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
                    token_count=self.tokenizer.count_tokens(prompt_stack),
                    prompt_stack=prompt_stack,
                    prompt=self.tokenizer.prompt_stack_to_string(prompt_stack),
                )
            )

    def after_run(self, result: PromptStackElement) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(
                    model=self.model, result=result.value, token_count=self.tokenizer.count_tokens(result.value)
                )
            )

    def run(self, prompt_stack: PromptStack) -> PromptStackElement:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                if self.stream:
                    tokens = []

                    partial_elements = self.try_stream(prompt_stack)

                    for partial_element in partial_elements:
                        if isinstance(partial_element.content_delta, TextDeltaPromptStackContent):
                            chunk_value = partial_element.content_delta.value
                            self.structure.publish_event(CompletionChunkEvent(token=chunk_value))
                            tokens.append(chunk_value)
                    content = TextPromptStackContent(value=TextArtifact("".join(tokens).strip()))
                    result = PromptStackElement(content=content, role=PromptStackElement.ASSISTANT_ROLE)
                else:
                    result = self.try_run(prompt_stack)

                self.after_run(result)

                return result
        else:
            raise Exception("prompt driver failed after all retry attempts")

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement: ...

    @abstractmethod
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[PartialPromptStackElement]: ...
