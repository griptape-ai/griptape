from warpspeed.utils import TiktokenTokenizer


class TestTiktokenTokenizer:
    def test_encode(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.encode("foo bar") == [21943, 2318]

    def test_decode(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.decode([21943, 2318]) == "foo bar"

    def test_token_count(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.token_count("foo bar huzzah") == 5

    def test_tokens_left(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.tokens_left("foo bar huzzah") == 3995

    def test_encoding(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.encoding.name == "p50k_base"
