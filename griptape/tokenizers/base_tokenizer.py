from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from attrs import Factory, define, field

from griptape.common import BasePromptStackContent, PromptStack, PromptStackElement


@define()
class BaseTokenizer(ABC):
    DEFAULT_MAX_INPUT_TOKENS = 4096
    DEFAULT_MAX_OUTPUT_TOKENS = 1000
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {}

    model: str = field(kw_only=True)
    stop_sequences: list[str] = field(default=Factory(list), kw_only=True)
    max_input_tokens: int = field(
        kw_only=True, default=Factory(lambda self: self._default_max_input_tokens(), takes_self=True)
    )
    max_output_tokens: int = field(
        kw_only=True, default=Factory(lambda self: self._default_max_output_tokens(), takes_self=True)
    )

    def count_input_tokens_left(self, text: str | PromptStack) -> int:
        diff = self.max_input_tokens - self.count_tokens(text)

        if diff > 0:
            return diff
        else:
            return 0

    def count_output_tokens_left(self, text: str | PromptStack) -> int:
        diff = self.max_output_tokens - self.count_tokens(text)

        if diff > 0:
            return diff
        else:
            return 0

    def count_tokens(self, text: str | PromptStack) -> int:
        if isinstance(text, PromptStack):
            return self.try_count_tokens(self.prompt_stack_to_string(text))
        else:
            return self.try_count_tokens(text)

    @abstractmethod
    def try_count_tokens(self, text: Any) -> int: ...

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        """Converts a Prompt Stack to a string for token counting or model input.
        This base implementation will not be very accurate, and should be overridden by subclasses with model-specific tokens.

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
    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        """Converts a PromptStack Input to a ChatML-style message dictionary for token counting or model input.

        Args:
            prompt_input: The PromptStack Input to convert.

        Returns:
            A dictionary with the role and content of the input.
        """
        ...

    @abstractmethod
    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> Any:
        """Converts a BasePromptStackContent to message content for token counting or model input.

        Args:
            content: The BasePromptStackContent to convert.

        Returns:
            A dictionary with the role and content of the input.
        """
        ...

    @abstractmethod
    def message_content_to_prompt_stack_content(self, message_content: Any) -> BasePromptStackContent:
        """Converts a message content dictionary to a BasePromptStackContent.

        Args:
            message_content: The message content dictionary to convert.

        Returns:
            A BasePromptStackContent instance.
        """
        ...

    def _default_max_input_tokens(self) -> int:
        tokens = next((v for k, v in self.MODEL_PREFIXES_TO_MAX_INPUT_TOKENS.items() if self.model.startswith(k)), None)

        if tokens is None:
            return self.DEFAULT_MAX_INPUT_TOKENS
        else:
            return tokens

    def _default_max_output_tokens(self) -> int:
        tokens = next(
            (v for k, v in self.MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS.items() if self.model.startswith(k)), None
        )

        if tokens is None:
            return self.DEFAULT_MAX_OUTPUT_TOKENS
        else:
            return tokens
