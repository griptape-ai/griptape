from os import environ

environ["TRANSFORMERS_VERBOSITY"] = "error"

import pytest
from transformers import GPT2Tokenizer
from griptape.tokenizers import HuggingFaceTokenizer


class TestHuggingFaceTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return HuggingFaceTokenizer(
            tokenizer=GPT2Tokenizer.from_pretrained("gpt2")
        )

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_tokens_left(self, tokenizer):
        assert tokenizer.count_tokens_left("foo bar huzzah") == 1019
