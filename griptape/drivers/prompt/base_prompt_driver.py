from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Callable, Optional

from attr import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.artifacts.action_chunk_artifact import ActionChunkArtifact
from griptape.artifacts.actions_artifact import ActionsArtifact
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.events.action_chunk_event import ActionChunkEvent
from griptape.mixins import ExponentialBackoffMixin
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.tokenizers import BaseTokenizer
from griptape.utils import PromptStack

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
    prompt_stack_to_string: Callable[[PromptStack], str] = field(
        default=Factory(lambda self: self.default_prompt_stack_to_string_converter, takes_self=True), kw_only=True
    )
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(lambda: (ImportError, ValueError)), kw_only=True
    )
    model: str = field(metadata={"serializable": True})
    tokenizer: BaseTokenizer
    stream: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    def max_output_tokens(self, text: str | list) -> int:
        tokens_left = self.tokenizer.count_output_tokens_left(text)

        if self.max_tokens:
            return min(self.max_tokens, tokens_left)
        else:
            return tokens_left

    def token_count(self, prompt_stack: PromptStack) -> int:
        return self.tokenizer.count_tokens(self.prompt_stack_to_string(prompt_stack))

    def before_run(self, prompt_stack: PromptStack) -> None:
        if self.structure:
            self.structure.publish_event(
                StartPromptEvent(
                    model=self.model,
                    token_count=self.token_count(prompt_stack),
                    prompt_stack=prompt_stack,
                    prompt=self.prompt_stack_to_string(prompt_stack),
                )
            )

    def after_run(self, result: TextArtifact) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(model=self.model, token_count=result.token_count(self.tokenizer), result=result.value)
            )

    def run(self, prompt_stack: PromptStack) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                if self.stream:
                    text_chunks = []
                    actions_chunks = {}

                    completion_chunks = self.try_stream(prompt_stack)
                    for chunk in completion_chunks:
                        if isinstance(chunk, ActionChunkArtifact):
                            if chunk.index in actions_chunks:
                                actions_chunks[chunk.index] += chunk
                            else:
                                actions_chunks[chunk.index] = chunk
                            self.structure.publish_event(
                                ActionChunkEvent(
                                    tag=chunk.tag, name=chunk.name, path=chunk.path, partial_input=chunk.partial_input
                                )
                            )
                        elif isinstance(chunk, TextArtifact):
                            text_chunks.append(chunk.value)
                            self.structure.publish_event(CompletionChunkEvent(token=chunk.value))

                    value = "".join(text_chunks).strip()
                    if actions_chunks:
                        actions = [
                            ActionsArtifact.Action(
                                tag=chunk.tag, name=chunk.name, path=chunk.path, input=json.loads(chunk.partial_input)
                            )
                            for chunk in actions_chunks.values()
                        ]
                        result = ActionsArtifact(value=value, actions=actions)
                    else:
                        result = TextArtifact(value=value)
                else:
                    result = self.try_run(prompt_stack)
                    result.value = result.value.strip()

                self.after_run(result)

                return result
        else:
            raise Exception("prompt driver failed after all retry attempts")

    def default_prompt_stack_to_string_converter(self, prompt_stack: PromptStack) -> str:
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
