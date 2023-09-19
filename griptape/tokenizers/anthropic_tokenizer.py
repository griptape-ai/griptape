import anthropic
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-2"
    DEFAULT_MAX_TOKENS = 100000

    model: str = field(default=DEFAULT_MODEL, kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def encode(self, text: str) -> list[int]:
        return anthropic._client.sync_get_tokenizer().encode(text).ids

    def decode(self, tokens: list[int]) -> str:
        return anthropic._client.sync_get_tokenizer().decode(tokens)
