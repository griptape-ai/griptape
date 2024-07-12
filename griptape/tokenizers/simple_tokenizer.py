from __future__ import annotations

from attrs import define, field

from griptape.tokenizers import BaseTokenizer


@define()
class SimpleTokenizer(BaseTokenizer):
    model: str = field(init=False, kw_only=True)
    characters_per_token: int = field(kw_only=True)

    def count_tokens(self, text: str) -> int:
        num_tokens = (len(text) + self.characters_per_token - 1) // self.characters_per_token

        return num_tokens
