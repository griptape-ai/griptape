from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer
from transformers import PreTrainedTokenizerFast

@define(frozen=True)
class TextGenTokenizer(BaseTokenizer):
    """
    Generic TextGenTokenizer that is a wrapper on PreTrainedTokenizerFast.

    'PreTrainedTokenizerFast' can be instantiated from a json file that usually is found in open source LLM models directories.
    LLM that text gen webui is working with.

    max_tokens = it's the value as defined in text gen preset or params.

    tokenizer = tokenizer instance. leaving this as None can cause a crash of this tokenizer.

    """

    max_tokens: int = field(
        default=200,
        kw_only=True
    )
    tokenizer: PreTrainedTokenizerFast = field(
        default=None,
        kw_only=True
    )

    def max_tokens(self) -> int:
        return self.max_tokens

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text=text)

    def decode(self, tokens: list[int]) -> str:
        return self.tokenizer.decode(token_ids=tokens)
