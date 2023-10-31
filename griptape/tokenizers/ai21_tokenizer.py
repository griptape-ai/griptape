import ai21
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class Ai21Tokenizer(BaseTokenizer):
    DEFAULT_MODEL = "j2-ultra"
    DEFAULT_MAX_TOKENS = 8192

    model: str = field(kw_only=True)
    api_key: str = field(kw_only=True)

    def __attrs_post_init__(self):
        ai21.api_key = self.api_key

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        response = ai21.Tokenization.execute(text=text)

        return len(response["tokens"])
