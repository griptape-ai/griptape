import pytest
from griptape.tokenizers import BedrockClaudeTokenizer


class TestBedrockClaudeTokenizer:
    @pytest.fixture
    def tokenizer(self, request):
        return BedrockClaudeTokenizer(model=request.param)

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [
            ("anthropic.claude-v2:1", 5),
            ("anthropic.claude-v2", 5),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 5),
            ("anthropic.claude-3-haiku-20240307-v1:0", 5),
        ],
        indirect=["tokenizer"],
    )
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [
            ("anthropic.claude-v2", 99995),
            ("anthropic.claude-v2:1", 199995),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 199995),
            ("anthropic.claude-3-haiku-20240307-v1:0", 199995),
        ],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [
            ("anthropic.claude-v2", 4091),
            ("anthropic.claude-v2:1", 4091),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 4091),
            ("anthropic.claude-3-haiku-20240307-v1:0", 4091),
        ],
        indirect=["tokenizer"],
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
