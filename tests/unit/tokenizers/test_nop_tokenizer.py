import pytest
from griptape.exceptions import NopException
from griptape.tokenizers import NopTokenizer


class TestNopTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return NopTokenizer()

    def test_token_count(self, tokenizer):
        with pytest.raises(NopException):
            tokenizer.count_tokens("foo bar huzzah")

    def test_tokens_left(self, tokenizer):
        with pytest.raises(NopException):
            tokenizer.count_tokens("foo bar huzzah")
