import pytest

from griptape.tokenizers import MinimaxTokenizer


class TestMinimaxTokenizer:
    def test_init(self):
        assert MinimaxTokenizer(model="MiniMax-M3")

    def test_count_tokens(self):
        tokenizer = MinimaxTokenizer(model="MiniMax-M3")

        assert tokenizer.count_tokens("foo bar huzzah") == 5

    @pytest.mark.parametrize(
        ("model", "context_window"),
        [
            ("MiniMax-M3", 1_000_000),
            ("MiniMax-M2.7", 204_800),
        ],
    )
    def test_max_input_tokens(self, model, context_window):
        tokenizer = MinimaxTokenizer(model=model)

        assert tokenizer.max_input_tokens == context_window - MinimaxTokenizer.TOKEN_OFFSET
