from __future__ import annotations
import ai21
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class Ai21Tokenizer(BaseTokenizer):
    DEFAULT_MODEL = "j2-ultra"
    DEFAULT_MAX_TOKENS = 8192

    model: str = field(kw_only=True)
    api_key: str = field(kw_only=True)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS, kw_only=True)

    def __attrs_post_init__(self):
        ai21.api_key = self.api_key

    def count_tokens(self, text: str | list[str]) -> int:
        if isinstance(text, str):
            response = ai21.Tokenization.execute(text=text)

            return len(response["tokens"])
        else:
            raise ValueError("Text must be a string.")
