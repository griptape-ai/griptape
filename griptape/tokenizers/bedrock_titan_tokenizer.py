from __future__ import annotations
from attr import define, field
from .base_tokenizer import BaseTokenizer
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockTitanTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "amazon.titan-text-express-v1"
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    DEFAULT_MAX_TOKENS = 4096

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
