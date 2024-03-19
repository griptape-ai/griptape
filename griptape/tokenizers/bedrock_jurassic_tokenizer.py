from __future__ import annotations
from attr import define, field, Factory
from .simple_tokenizer import SimpleTokenizer


@define()
class BedrockJurassicTokenizer(SimpleTokenizer):
    DEFAULT_CHARACTERS_PER_TOKEN = 6  # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"ai21": 8192}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {
        "ai21.j2-mid-v1": 8191,
        "ai21.j2-ultra-v1": 8191,
        "ai21.j2-large-v1": 8191,
        "ai21": 2048,
    }

    model: str = field(kw_only=True)
    characters_per_token: int = field(
        default=Factory(lambda self: self.DEFAULT_CHARACTERS_PER_TOKEN, takes_self=True), kw_only=True
    )
