import pytest
from griptape.tokenizers import AnthropicTokenizer


class TestAnthropicTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return AnthropicTokenizer(model=AnthropicTokenizer.DEFAULT_MODEL)

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_tokens_left(self, tokenizer):
        assert tokenizer.count_tokens_left("foo bar huzzah") == 99995
