from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client


@define(frozen=True)
class CohereTokenizer(BaseTokenizer):
    # https://docs.cohere.com/docs/models
    MODEL_PREFIXES_TO_MAX_TOKENS = {
        "command": 4096,
        "embed-english": 512,
        "embed-multilingual-v2.0": 256,
        "embed-multilingual": 512,
    }

    model: str = field(kw_only=True)
    client: Client = field(kw_only=True)
    max_tokens: int = field(default=Factory(lambda self: self.default_max_tokens(), takes_self=True), kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            return len(self.client.tokenize(text=text).tokens)
        else:
            raise ValueError("Text must be a string.")

    def default_max_tokens(self) -> int:
        tokens = next(v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model.startswith(k))

        return tokens
