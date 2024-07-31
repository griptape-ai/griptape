from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.common import (
        DeltaMessage,
        Message,
        PromptStack,
    )
    from griptape.tokenizers import BaseTokenizer


@define(kw_only=True)
class BasePromptDriver(SerializableMixin, ABC):
    """Base class for the Prompt Drivers.

    Attributes:
        temperature: The temperature to use for the completion.
        max_tokens: The maximum number of tokens to generate. If not specified, the value will be automatically generated based by the tokenizer.
        prompt_stack_to_string: A function that converts a `PromptStack` to a string.
        ignored_exception_types: A tuple of exception types to ignore.
        model: The model name.
        tokenizer: An instance of `BaseTokenizer` to when calculating tokens.
        stream: Whether to stream the completion or not. `CompletionChunkEvent`s will be published to the `Structure` if one is provided.
        use_native_tools: Whether to use LLM's native function calling capabilities. Must be supported by the model.
    """

    temperature: float = field(default=0.1, metadata={"serializable": True})
    max_tokens: Optional[int] = field(default=None, metadata={"serializable": True})
    ignored_exception_types: tuple[type[Exception], ...] = field(default=Factory(lambda: (ImportError, ValueError)))
    model: str = field(metadata={"serializable": True})
    tokenizer: BaseTokenizer
    use_native_tools: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    @abstractmethod
    def run(self, prompt_stack: PromptStack) -> Message: ...

    @abstractmethod
    def stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]: ...

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
