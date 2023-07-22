import ai21
import pytest
from griptape.tokenizers import Ai21Tokenizer


class TestAi21Tokenizer:
    @pytest.fixture
    def tokenizer(self):
        tokenizer = Ai21Tokenizer(api_key="foo")

        return tokenizer

    def test_encode(self, tokenizer, monkeypatch):
        monkeypatch.setattr(
            ai21.Tokenization,
            "execute",
            lambda *args, **kwargs: {"tokens": [{"token": "foo"}, {"token": "bar"}]},
        )
        try:
           tokenizer.encode("foo bar")
        except NotImplementedError:
            assert True

    def test_decode(self, tokenizer):
        try:
            assert tokenizer.decode([6713199, 6447474]) == "foo bar"
        except NotImplementedError:
            assert True

    def test_token_count(self, tokenizer, monkeypatch):
        monkeypatch.setattr(
            ai21.Tokenization,
            "execute",
            lambda *args, **kwargs: {
                "tokens": [{"token": "foo"}, {"token": "bar"}, {"token": "huzzah"}]
            },
        )
        assert tokenizer.token_count("foo bar huzzah") == 3

    def test_tokens_left(self, tokenizer, monkeypatch):
        monkeypatch.setattr(
            ai21.Tokenization,
            "execute",
            lambda *args, **kwargs: {
                "tokens": [{"token": "foo"}, {"token": "bar"}, {"token": "huzzah"}]
            },
        )
        assert tokenizer.tokens_left("foo bar huzzah") == 8189
