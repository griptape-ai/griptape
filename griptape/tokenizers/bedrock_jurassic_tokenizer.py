from __future__ import annotations
from attr import define, field, Factory
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockJurassicTokenizer(SimpleTokenizer):
    DEFAULT_MODEL = "ai21.j2-ultra-v1"
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning

    characters_per_token: int = field(
        default=Factory(lambda self: self.DEFAULT_CHARACTERS_PER_TOKEN, takes_self=True), kw_only=True
    )
    max_tokens: int = field(default=Factory(lambda self: self.DEFAULT_MAX_TOKENS, takes_self=True), kw_only=True)
    model: str = field(kw_only=True)
