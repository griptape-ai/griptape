from __future__ import annotations
from attrs import define, field
from .simple_tokenizer import SimpleTokenizer


@define()
class BedrockCohereTokenizer(SimpleTokenizer):
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-embed.html
    DEFAULT_CHARACTERS_PER_TOKEN = 4
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"cohere": 1024}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"cohere": 4096}

    model: str = field(kw_only=True)
    characters_per_token: int = field(default=DEFAULT_CHARACTERS_PER_TOKEN, kw_only=True)
