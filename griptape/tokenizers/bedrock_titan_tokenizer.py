from __future__ import annotations
from attr import define, field
from griptape.tokenizers import BaseTokenizer, SimpleTokenizer


@define(frozen=True)
class BedrockTitanTokenizer(BaseTokenizer):
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    DEFAULT_MAX_TOKENS = 4096

    DEFAULT_EMBEDDING_MODELS = "amazon.titan-embed-text-v1"

    tokenizer: SimpleTokenizer = field(
        default=SimpleTokenizer(max_tokens=DEFAULT_MAX_TOKENS, characters_per_token=DEFAULT_CHARACTERS_PER_TOKEN),
        kw_only=True,
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        return self.tokenizer.count_tokens(text)
