import pytest

from griptape.tokenizers import AmazonBedrockTokenizer


class TestAmazonBedrockTokenizer:
    @pytest.fixture()
    def tokenizer(self, request):
        return AmazonBedrockTokenizer(model=request.param)

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("anthropic.claude-v2:1", 4),
            ("anthropic.claude-v2", 4),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 4),
            ("anthropic.claude-3-haiku-20240307-v1:0", 4),
        ],
        indirect=["tokenizer"],
    )
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("anthropic.claude-v2", 99996),
            ("anthropic.claude-v2:1", 199996),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 199996),
            ("anthropic.claude-3-haiku-20240307-v1:0", 199996),
        ],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("anthropic.claude-v2", 4092),
            ("anthropic.claude-v2:1", 4092),
            ("anthropic.claude-3-sonnet-20240229-v1:0", 4092),
            ("anthropic.claude-3-haiku-20240307-v1:0", 4092),
        ],
        indirect=["tokenizer"],
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
