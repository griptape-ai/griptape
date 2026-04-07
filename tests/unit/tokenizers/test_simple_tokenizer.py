import pytest

from griptape.tokenizers import SimpleTokenizer


class TestSimpleTokenizer:
    @pytest.fixture()
    def tokenizer(self):
        return SimpleTokenizer(max_input_tokens=1024, max_output_tokens=4096, characters_per_token=6)

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 3

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == 1021

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == 4093
