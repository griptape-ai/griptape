from __future__ import annotations

from attrs import define

from griptape.tokenizers import BaseTokenizer


@define()
class MockTokenizer(BaseTokenizer):
    def count_tokens(self, text: str) -> int:
        return len(text)
