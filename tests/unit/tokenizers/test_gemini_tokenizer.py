import pytest
from unittest import mock
from griptape.tokenizers import GeminiTokenizer
from vertexai.preview.generative_models import GenerativeModel


class TestGeminiTokenizer:
    @pytest.fixture(autouse=True)
    def mock_gemini(self):
        mock_gemini = mock.Mock(GenerativeModel)
        mock_gemini.count_tokens.return_value = mock.Mock(total_tokens=5)

        return mock_gemini

    @pytest.fixture
    def tokenizer(self, request, mock_gemini):
        return GeminiTokenizer(model=request.param, gemini=mock_gemini)

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
