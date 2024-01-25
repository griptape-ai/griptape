from __future__ import annotations
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class SimpleTokenizer(BaseTokenizer):
    characters_per_token: int = field(kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            num_tokens = (len(text) + self.characters_per_token - 1) // self.characters_per_token

            return num_tokens
        else:
            raise ValueError("Text must be a string.")
