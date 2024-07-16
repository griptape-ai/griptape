from os import environ

environ["TRANSFORMERS_VERBOSITY"] = "error"

import pytest  # noqa: E402

from griptape.tokenizers import HuggingFaceTokenizer  # noqa: E402


class TestHuggingFaceTokenizer:
    @pytest.fixture()
    def tokenizer(self):
        return HuggingFaceTokenizer(model="gpt2", max_output_tokens=1024)

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == 1019

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == 1019
