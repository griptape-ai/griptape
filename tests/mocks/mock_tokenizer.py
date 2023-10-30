from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class MockTokenizer(BaseTokenizer):
    model: str = field(kw_only=True)
    max_tokens: int = field(default=1000, kw_only=True)

    def count_tokens(self, text: str) -> int:
        return len(text)
