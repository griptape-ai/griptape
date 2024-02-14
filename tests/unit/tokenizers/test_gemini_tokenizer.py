import pytest
from griptape.tokenizers import GeminiTokenizer


class TestGeminiTokenizer:
    def test_token_count(self):
        tokenizer = GeminiTokenizer()
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_tokens_left(self):
        tokenizer = GeminiTokenizer()
        assert tokenizer.count_tokens_left("foo bar huzzah") == 30715

    def test_token_count_vision(self):
        tokenizer = GeminiTokenizer(model=GeminiTokenizer.DEFAULT_GEMINI_VISION_MODEL)
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_tokens_left_vision(self):
        tokenizer = GeminiTokenizer(model=GeminiTokenizer.DEFAULT_GEMINI_VISION_MODEL)
        assert tokenizer.count_tokens_left("foo bar huzzah") == 12283
