from __future__ import annotations
from attr import define, field, Factory
from .simple_tokenizer import SimpleTokenizer


@define(frozen=True)
class BedrockJurassicTokenizer(SimpleTokenizer):
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html#model-customization-prepare-finetuning
    DEFAULT_CHARACTERS_PER_TOKEN = 6
    MODEL_PREFIXES_TO_MAX_TOKENS = {"ai21.j2": 8191}

    model: str = field(kw_only=True)
    characters_per_token: int = field(
        default=Factory(lambda self: self.DEFAULT_CHARACTERS_PER_TOKEN, takes_self=True), kw_only=True
    )
    max_tokens: int = field(default=Factory(lambda self: self.default_max_tokens(), takes_self=True), kw_only=True)

    def default_max_tokens(self) -> int:
        tokens = next(v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model.startswith(k))

        return tokens
