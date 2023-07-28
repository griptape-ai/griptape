from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer
from transformers import PreTrainedTokenizerBase


@define(frozen=True)
class TextGenTokenizer(BaseTokenizer):
    """
    Generic TextGenTokenizer that is a wrapper on PreTrainedTokenizerFast.

    'PreTrainedTokenizerFast' can be instantiated from a json file that usually is found in open source LLM models directories.
    LLM that text gen webui is working with.

    max_tokens = it's the value as defined in text gen preset or params.

    tokenizer = tokenizer instance. leaving this as None can cause a crash of this tokenizer.

    """

    tokenizer: PreTrainedTokenizerBase = field(
        kw_only=True
    )

    @property
    def max_tokens(self) -> int:
        return self.tokenizer.model_max_length

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text=text)

    def decode(self, tokens: list[int]) -> str:
        return self.tokenizer.decode(token_ids=tokens)
