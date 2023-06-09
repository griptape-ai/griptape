import pytest
from griptape.tokenizers import AnthropicTokenizer


class TestAnthropicTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return AnthropicTokenizer()

    def test_encode(self, tokenizer):
        assert tokenizer.encode("foo bar") == [3803, 3871]

    def test_decode(self, tokenizer):
        assert tokenizer.decode([3803, 3871]) == "foo bar"

    def test_token_count(self, tokenizer):
        assert tokenizer.token_count("foo bar huzzah") == 5

    def test_tokens_left(self, tokenizer):
        assert tokenizer.tokens_left("foo bar huzzah") == 99995
