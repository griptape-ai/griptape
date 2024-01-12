from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase


@define(frozen=True)
class HuggingFaceTokenizer(BaseTokenizer):
    tokenizer: PreTrainedTokenizerBase = field(kw_only=True)
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.model_max_length, takes_self=True), kw_only=True
    )

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            return len(self.tokenizer.encode(text))
        else:
            raise ValueError("Text must be a string.")
