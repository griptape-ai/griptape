import anthropic
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-v1"
    DEFAULT_MAX_TOKENS = 8000
    MODEL_TO_MAX_TOKENS = {
        "claude-v1": 8000,
        "claude-v1-100k": 100000,
        "claude-instant-v1": 8000,
        "claude-instant-v1-100k": 100000,
        "claude-v1.3": 8000,
        "claude-v1.3-100k": 100000,
        "claude-v1.2": 8000,
        "claude-v1.0": 8000,
        "claude-instant-v1.1": 8000,
        "claude-instant-v1.1-100k": 100000,
        "claude-instant-v1.0": 8000,
    }

    model: str = field(default=DEFAULT_MODEL, kw_only=True)

    @property
    def max_tokens(self) -> int:
        return (
            self.MODEL_TO_MAX_TOKENS[self.model]
            if self.model in self.MODEL_TO_MAX_TOKENS
            else self.DEFAULT_MAX_TOKENS
        )

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def encode(self, text: str) -> list[int]:
        return anthropic.get_tokenizer().encode(text)

    def decode(self, tokens: list[int]) -> str:
        return anthropic.get_tokenizer().decode(tokens)
