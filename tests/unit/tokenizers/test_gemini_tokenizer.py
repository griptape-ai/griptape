import pytest
from attr import field, define
from griptape.tokenizers import GeminiTokenizer
from vertexai.preview.generative_models import GenerativeModel


@define
class MockTokenCount:
    total_tokens: int = field(default=5, kw_only=True)


class MockGenerativeModel(GenerativeModel):

    def __init__(self):
        pass

    def count_tokens(self, text: str) -> MockTokenCount:
        return MockTokenCount(total_tokens=5)


class TestGeminiTokenizer:

    @pytest.fixture
    def mock_gemini(self):
        return MockGenerativeModel()

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
