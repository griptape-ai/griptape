from __future__ import annotations
from attr import define, field, Factory
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-2"
    DEFAULT_MAX_TOKENS = 100000

    model: str = field(kw_only=True)
    max_tokens: int = field(default=Factory(lambda self: self.DEFAULT_MAX_TOKENS, takes_self=True), kw_only=True)

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str):
            anthropic = import_optional_dependency("anthropic")

            return len(anthropic._client.sync_get_tokenizer().encode(text).ids)
        else:
            raise ValueError("Text must be a string.")
