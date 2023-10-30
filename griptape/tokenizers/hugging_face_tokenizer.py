from os import environ

environ["TRANSFORMERS_VERBOSITY"] = "error"

from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer
from transformers import PreTrainedTokenizerBase


@define(frozen=True)
class HuggingFaceTokenizer(BaseTokenizer):
    tokenizer: PreTrainedTokenizerBase = field(kw_only=True)
    max_tokens: int = field(
        default=Factory(
            lambda self: self.tokenizer.model_max_length, takes_self=True
        ),
        kw_only=True,
    )

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
