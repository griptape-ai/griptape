import cohere
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class CohereTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "command"
    MAX_TOKENS = 2048

    model: str = field(kw_only=True)
    client: cohere.Client = field(kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        return len(self.client.tokenize(text=text).tokens)
