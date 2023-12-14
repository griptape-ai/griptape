from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from anthropic import Anthropic


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-2.1"
    MODEL_PREFIXES_TO_MAX_TOKENS = {"claude-2.1": 200000, "claude": 100000}

    model: str = field(kw_only=True)
    client: Anthropic = field(default=import_optional_dependency("anthropic").Anthropic(), kw_only=True)

    @property
    def max_tokens(self) -> int:
        tokens = next(v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model.startswith(k))

        return tokens

    def count_tokens(self, text: str) -> int:
        return self.client.count_tokens(text)
