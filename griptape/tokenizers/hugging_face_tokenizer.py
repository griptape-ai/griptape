from __future__ import annotations
from typing import TYPE_CHECKING
from os import environ

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase

environ["TRANSFORMERS_VERBOSITY"] = "error"

from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class HuggingFaceTokenizer(BaseTokenizer):
    tokenizer: PreTrainedTokenizerBase = field(kw_only=True)
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.model_max_length, takes_self=True), kw_only=True
    )

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
