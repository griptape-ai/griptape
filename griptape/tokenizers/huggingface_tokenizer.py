from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.common import BasePromptStackContent, PromptStack, PromptStackElement, TextPromptStackContent
from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase


@define()
class HuggingFaceTokenizer(BaseTokenizer):
    tokenizer: PreTrainedTokenizerBase = field(
        default=Factory(
            lambda self: import_optional_dependency("transformers").AutoTokenizer.from_pretrained(self.model),
            takes_self=True,
        ),
        kw_only=True,
    )
    max_input_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.model_max_length, takes_self=True), kw_only=True
    )
    max_output_tokens: int = field(default=4096, kw_only=True)

    def count_tokens(self, text: str | PromptStack) -> int:
        if isinstance(text, PromptStack):
            tokens = self.__prompt_stack_to_tokens(text)

            return len(tokens)
        else:
            return self.try_count_tokens(text)

    def try_count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.decode(self.__prompt_stack_to_tokens(prompt_stack))

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        if len(prompt_input.content) == 1:
            return {
                "role": prompt_input.role,
                "content": self.prompt_stack_content_to_message_content(prompt_input.content[0]),
            }
        else:
            raise ValueError("HuggingFace does not support multiple prompt stack contents.")

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> str:
        if isinstance(content, TextPromptStackContent):
            return content.artifact.value
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __prompt_stack_to_tokens(self, prompt_stack: PromptStack) -> list[int]:
        tokens = self.tokenizer.apply_chat_template(
            [self.prompt_stack_input_to_message(i) for i in prompt_stack.inputs],
            add_generation_prompt=True,
            tokenize=True,
        )

        if isinstance(tokens, list):
            return tokens
        else:
            raise ValueError("Invalid output type.")
