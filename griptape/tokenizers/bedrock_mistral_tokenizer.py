from __future__ import annotations
from attr import define, field
from .simple_tokenizer import SimpleTokenizer


@define()
class BedrockMistralTokenizer(SimpleTokenizer):
    DEFAULT_CHARACTERS_PER_TOKEN = 6
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"mistral": 32000}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"mistral.mistral-7b-instruct": 8192, "mistral.mixtral-8x7b-instruct": 4096}

    model: str = field(kw_only=True)
    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
