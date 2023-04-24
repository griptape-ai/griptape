import pytest
from transformers import GPT2Tokenizer
from griptape.tokenizers import HuggingFaceTokenizer


class TestHuggingFaceTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return HuggingFaceTokenizer(
            tokenizer=GPT2Tokenizer.from_pretrained("gpt2")
        )

    def test_encode(self, tokenizer):
        assert tokenizer.encode("foo bar") == [21943, 2318]

    def test_decode(self, tokenizer):
        assert tokenizer.decode([21943, 2318]) == "foo bar"

    def test_token_count(self, tokenizer):
        assert tokenizer.token_count("foo bar huzzah") == 5

    def test_tokens_left(self, tokenizer):
        assert tokenizer.tokens_left("foo bar huzzah") == 1019
