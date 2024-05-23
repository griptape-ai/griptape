from __future__ import annotations
from attrs import define, field
from .simple_tokenizer import SimpleTokenizer


@define()
class BedrockLlamaTokenizer(SimpleTokenizer):
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"meta": 2048}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"meta": 2048}

    model: str = field(kw_only=True)
    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
    stop_sequences: list[str] = field(factory=list, kw_only=True)
