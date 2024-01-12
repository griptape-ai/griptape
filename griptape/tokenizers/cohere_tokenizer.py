from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client


@define(frozen=True)
class CohereTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "command"
    DEFAULT_MAX_TOKENS = 2048

    model: str = field(kw_only=True)
    client: Client = field(kw_only=True)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS, kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            return len(self.client.tokenize(text=text).tokens)
        else:
            raise ValueError("Text must be a string.")
