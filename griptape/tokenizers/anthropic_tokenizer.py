from attr import define, field
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AnthropicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "claude-2"
    DEFAULT_MAX_TOKENS = 100000

    model: str = field(kw_only=True)

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        anthropic = import_optional_dependency("anthropic")

        return len(anthropic._client.sync_get_tokenizer().encode(text).ids)
