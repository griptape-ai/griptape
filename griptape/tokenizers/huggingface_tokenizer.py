from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field, Factory
from griptape.utils import PromptStack
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase


@define()
class HuggingFaceTokenizer(BaseTokenizer):
    tokenizer: PreTrainedTokenizerBase = field(kw_only=True)
    model: None = field(init=False, default=None, kw_only=True)
    max_input_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.model_max_length, takes_self=True), kw_only=True
    )
    max_output_tokens: int = field(kw_only=True)  # pyright: ignore[reportGeneralTypeIssues]

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

    def prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        return {"role": prompt_input.role, "content": prompt_input.content}

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
