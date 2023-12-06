from __future__ import annotations
from attr import define, field
from .base_tokenizer import BaseTokenizer
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockJurassicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "ai21.j2-ultra-v1"
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning

    model: str = field(kw_only=True)
    tokenizer: SimpleTokenizer = field(
        default=SimpleTokenizer(max_tokens=DEFAULT_MAX_TOKENS, characters_per_token=DEFAULT_CHARACTERS_PER_TOKEN),
        kw_only=True,
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        return self.tokenizer.count_tokens(text)
