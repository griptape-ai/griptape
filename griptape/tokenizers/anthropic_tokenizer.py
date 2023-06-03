import anthropic
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-v1"
    MAX_TOKENS = 8000

    model: str = field(default=DEFAULT_MODEL, kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.MAX_TOKENS

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def encode(self, text: str) -> list[int]:
        return anthropic.get_tokenizer().encode(text)

    def decode(self, tokens: list[int]) -> str:
        return anthropic.get_tokenizer().detokenize(tokens=tokens)
