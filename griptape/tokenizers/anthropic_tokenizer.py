import anthropic
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-v1"
    DEFAULT_MAX_TOKENS = 8000
    MODEL_SUFFIXES_TO_MAX_TOKENS = {
        "100k": 100000,
    }

    model: str = field(default=DEFAULT_MODEL, kw_only=True)

    @property
    def max_tokens(self) -> int:
        for suffix, token_limit in self.MODEL_SUFFIXES_TO_MAX_TOKENS.items():
            if self.model.endswith(suffix):
                return token_limit
        return self.DEFAULT_MAX_TOKENS

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def encode(self, text: str) -> list[int]:
        return anthropic.get_tokenizer().encode(text)

    def decode(self, tokens: list[int]) -> str:
        return anthropic.get_tokenizer().decode(tokens)
