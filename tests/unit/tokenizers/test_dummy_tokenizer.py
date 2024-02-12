import pytest
from griptape.exceptions import DummyException
from griptape.tokenizers import DummyTokenizer


class TestDummyTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return DummyTokenizer()

    def test_token_count(self, tokenizer):
        with pytest.raises(DummyException):
            tokenizer.count_tokens("foo bar huzzah")

    def test_tokens_left(self, tokenizer):
        with pytest.raises(DummyException):
            tokenizer.count_tokens("foo bar huzzah")
