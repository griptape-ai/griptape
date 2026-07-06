from griptape.tokenizers import MinimaxTokenizer


class TestMinimaxTokenizer:
    def test_init(self):
        assert MinimaxTokenizer(model="MiniMax-M3")

    def test_count_tokens(self):
        tokenizer = MinimaxTokenizer(model="MiniMax-M3")

        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_max_input_tokens(self):
        tokenizer = MinimaxTokenizer(model="MiniMax-M3")

        assert tokenizer.max_input_tokens == 1000000 - MinimaxTokenizer.TOKEN_OFFSET
