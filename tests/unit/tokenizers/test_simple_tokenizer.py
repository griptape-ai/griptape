import pytest
from griptape.tokenizers import SimpleTokenizer


class TestSimpleTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return SimpleTokenizer(max_tokens=1024, characters_per_token=6)

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 3

    def test_tokens_left(self, tokenizer):
        assert tokenizer.count_tokens_left("foo bar huzzah") == 1021
