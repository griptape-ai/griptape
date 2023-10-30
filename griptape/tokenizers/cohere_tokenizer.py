from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client


@define(frozen=True)
class CohereTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "command"
    MAX_TOKENS = 2048

    model: str = field(kw_only=True)
    client: Client = field(kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        return len(self.client.tokenize(text=text).tokens)
