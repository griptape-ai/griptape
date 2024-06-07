from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from attrs import Factory, define, field

from griptape.common import PromptStack, PromptStackElement
from griptape.common import BasePromptStackContent
from griptape.common import TextPromptStackContent
from griptape.common import ImagePromptStackContent


@define()
class BaseTokenizer(ABC):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {}

    model: str = field(kw_only=True)
    stop_sequences: list[str] = field(default=Factory(list), kw_only=True)
    max_input_tokens: int = field(kw_only=True, default=None)
    max_output_tokens: int = field(kw_only=True, default=None)

    def __attrs_post_init__(self) -> None:
        if self.max_input_tokens is None:
            self.max_input_tokens = self._default_max_input_tokens()

        if self.max_output_tokens is None:
            self.max_output_tokens = self._default_max_output_tokens()

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

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        """Converts a PromptStack Input to a ChatML-style message dictionary for token counting or model input.

        Args:
            prompt_input: The PromptStack Input to convert.

        Returns:
            A dictionary with the role and content of the input.
        """

        if isinstance(prompt_input.content, BasePromptStackContent):
            message_content = str(prompt_input.content)
        else:
            message_content = [self.prompt_stack_content_to_message(content) for content in prompt_input.content]

        if prompt_input.is_system():
            return {"role": "system", "content": message_content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": message_content}
        else:
            return {"role": "user", "content": message_content}

    def prompt_stack_content_to_message(self, content: BasePromptStackContent) -> dict | list[dict]:
        """Converts a BasePromptStackContent to a ChatML-style message dictionary for token counting or model input.

        Args:
            content: The BasePromptStackContent to convert.

        Returns:
            A dictionary with the role and content of the input.
        """
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.value.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {"type": "image", "image_url": {"url": f"data:image/jpeg;base64,{content.value.base64}"}}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def _default_max_input_tokens(self) -> int:
        tokens = next((v for k, v in self.MODEL_PREFIXES_TO_MAX_INPUT_TOKENS.items() if self.model.startswith(k)), None)

        if tokens is None:
            raise ValueError(f"Unknown model default max input tokens: {self.model}")
        else:
            return tokens

    def _default_max_output_tokens(self) -> int:
        tokens = next(
            (v for k, v in self.MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS.items() if self.model.startswith(k)), None
        )

        if tokens is None:
            raise ValueError(f"Unknown model for default max output tokens: {self.model}")
        else:
            return tokens
