from __future__ import annotations
from attrs import define, field
from griptape.exceptions import DummyException
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class DummyTokenizer(BaseTokenizer):
    max_tokens: int = field(default=float("inf"), kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        raise DummyException(__class__.__name__, "count_tokens")
