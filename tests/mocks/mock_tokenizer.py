from __future__ import annotations
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define()
class MockTokenizer(BaseTokenizer):
    model: str = field(kw_only=True)
    max_input_tokens: int = field(default=1000, kw_only=True)
    max_output_tokens: int = field(default=1000, kw_only=True)

    def count_tokens(self, text: str | list[dict]) -> int:
        return len(text)
