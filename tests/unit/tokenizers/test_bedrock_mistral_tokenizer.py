import pytest
from griptape.tokenizers import BedrockMistralTokenizer


class TestBedrockMistralTokenizer:
    @pytest.fixture
    def tokenizer(self, request):
        return BedrockMistralTokenizer(model=request.param)

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [("mistral.mistral-7b-instruct", 31997), ("mistral.mixtral-8x7b-instruct", 31997)],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [("mistral.mistral-7b-instruct", 8189), ("mistral.mixtral-8x7b-instruct", 4093)],
        indirect=["tokenizer"],
    )
    def test_ouput_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
