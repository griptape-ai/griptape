import ai21
import pytest
from griptape.tokenizers import Ai21Tokenizer


class TestAi21Tokenizer:
    @pytest.fixture
    def tokenizer(self):
        tokenizer = Ai21Tokenizer(
            model=Ai21Tokenizer.DEFAULT_MODEL, api_key="foo"
        )

        return tokenizer

    def test_count_tokens(self, tokenizer, monkeypatch):
        monkeypatch.setattr(
            ai21.Tokenization,
            "execute",
            lambda *args, **kwargs: {
                "tokens": [
                    {"token": "foo"},
                    {"token": "bar"},
                    {"token": "huzzah"},
                ]
            },
        )
        assert tokenizer.count_tokens("foo bar huzzah") == 3

    def test_count_tokens_left(self, tokenizer, monkeypatch):
        monkeypatch.setattr(
            ai21.Tokenization,
            "execute",
            lambda *args, **kwargs: {
                "tokens": [
                    {"token": "foo"},
                    {"token": "bar"},
                    {"token": "huzzah"},
                ]
            },
        )
        assert tokenizer.count_tokens_left("foo bar huzzah") == 8189
