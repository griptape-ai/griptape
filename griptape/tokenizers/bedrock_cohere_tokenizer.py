from __future__ import annotations
from attr import define, field
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockCohereTokenizer(SimpleTokenizer):
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-embed.html
    DEFAULT_CHARACTERS_PER_TOKEN = 4
    DEFAULT_MAX_TOKENS = 512

    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS, kw_only=True)
