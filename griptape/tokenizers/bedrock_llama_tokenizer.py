from __future__ import annotations
from attr import define, field
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockLlamaTokenizer(SimpleTokenizer):
    DEFAULT_MODEL = "meta.llama2-13b-chat-v1"
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    DEFAULT_MAX_TOKENS = 2048

    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS, kw_only=True)
    stop_sequences: list[str] = field(factory=list, kw_only=True)
    model: str = field(kw_only=True)
