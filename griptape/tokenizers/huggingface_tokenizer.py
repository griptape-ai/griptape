from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field, Factory
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

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            return len(self.tokenizer.encode(text))
        else:
            raise ValueError("Text must be a string.")
