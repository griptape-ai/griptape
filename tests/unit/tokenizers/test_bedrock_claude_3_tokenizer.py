import pytest
from griptape.tokenizers import BedrockClaude3Tokenizer


class TestBedrockClaude3Tokenizer:
    @pytest.fixture
    def tokenizer(self, request):
        return BedrockClaude3Tokenizer(model=request.param)

    @pytest.mark.parametrize(
        "tokenizer,expected", [("anthropic.claude-3-sonnet-20240229-v1:0", 5)], indirect=["tokenizer"]
    )
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected", [("anthropic.claude-3-sonnet-20240229-v1:0", 199995)], indirect=["tokenizer"]
    )
    def test_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_tokens_left("foo bar huzzah") == expected
