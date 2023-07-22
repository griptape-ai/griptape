import ai21
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class Ai21Tokenizer(BaseTokenizer):
    DEFAULT_MODEL = "j2-ultra"
    MAX_TOKENS = 8192

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    api_key: str = field(kw_only=True)

    def __attrs_post_init__(self):
        ai21.api_key = self.api_key

    @property
    def max_tokens(self) -> int:
        return self.MAX_TOKENS

    def token_count(self, text: str) -> int:
        response = ai21.Tokenization.execute(text=text)

        return len(response["tokens"])

    def encode(self, text: str) -> list[int]:
        raise NotImplementedError(
            "Method is not implemented: ai21 does not provide a compatible tokenization API"
        )

    def decode(self, tokens: list[int]) -> str:
        raise NotImplementedError(
            "Method is not implemented: ai21 does not provide a de-tokenization API"
        )
