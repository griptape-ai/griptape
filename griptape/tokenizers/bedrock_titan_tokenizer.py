from __future__ import annotations
from attr import define, field, Factory
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockTitanTokenizer(SimpleTokenizer):
    DEFAULT_MODEL = "amazon.titan-text-express-v1"
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    DEFAULT_MAX_TOKENS = 4096

    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS, kw_only=True)
    stop_sequences: list[str] = field(default=Factory(lambda: ["User:"]), kw_only=True)
    model: str = field(kw_only=True)
