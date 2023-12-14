import pytest
from griptape.tokenizers import AnthropicTokenizer


class TestAnthropicTokenizer:
    @pytest.fixture
    def tokenizer(self, request):
        return AnthropicTokenizer(model=request.param)

    @pytest.mark.parametrize("tokenizer,expected", [("claude-2.1", 5), ("claude-2.0", 5)], indirect=["tokenizer"])
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected", [("claude-2.1", 199995), ("claude-2.0", 99995)], indirect=["tokenizer"]
    )
    def test_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_tokens_left("foo bar huzzah") == expected
