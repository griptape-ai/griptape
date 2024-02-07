from __future__ import annotations
from attrs import define, field
from griptape.exceptions import NopException
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class NopTokenizer(BaseTokenizer):
    max_tokens: int = field(default=float("inf"), kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        raise NopException(__class__.__name__, "count_tokens")
