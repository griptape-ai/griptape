import pytest

from griptape.tokenizers import MinimaxTokenizer


class TestMinimaxTokenizer:
    def test_init(self):
        assert MinimaxTokenizer(model="MiniMax-M3")

    def test_count_tokens(self):
        tokenizer = MinimaxTokenizer(model="MiniMax-M3")

        assert tokenizer.count_tokens("foo bar huzzah") == 5

    @pytest.mark.parametrize(
        ("model", "context_window", "max_output_tokens"),
        [
            ("MiniMax-M3", 1_000_000, 524_288),
            ("MiniMax-M2.7", 204_800, 204_800),
        ],
    )
    def test_token_limits(self, model, context_window, max_output_tokens):
        tokenizer = MinimaxTokenizer(model=model)

        assert tokenizer.max_input_tokens == context_window - MinimaxTokenizer.TOKEN_OFFSET
        assert tokenizer.max_output_tokens == max_output_tokens
