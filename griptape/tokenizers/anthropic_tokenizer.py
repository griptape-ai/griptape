import anthropic
from attr import define, field
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-2"
    MODEL_TO_MAX_TOKENS = {
        "claude-2": 100000,
        "anthropic.claude-v2": 8192
    }
    
    model: str = field(default=DEFAULT_MODEL, kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.MODEL_TO_MAX_TOKENS[self.model]

    def encode(self, text: str) -> list[int]:
        return anthropic._client.sync_get_tokenizer().encode(text).ids

    def decode(self, tokens: list[int]) -> str:
        return anthropic._client.sync_get_tokenizer().decode(tokens)
