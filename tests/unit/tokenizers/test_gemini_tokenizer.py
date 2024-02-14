import pytest
from griptape.tokenizers import GeminiTokenizer


class TestGeminiTokenizer:
    @pytest.fixture
    def tokenizer(self, request):
        return GeminiTokenizer(model=request.param)

    @pytest.mark.parametrize(
        "tokenizer,expected", [("gemini-pro", 5), ("gemini-pro-vision", 5)], indirect=["tokenizer"]
    )
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected", [("gemini-pro", 30715), ("gemini-pro-vision", 12283)], indirect=["tokenizer"]
    )
    def test_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_tokens_left("foo bar huzzah") == expected
