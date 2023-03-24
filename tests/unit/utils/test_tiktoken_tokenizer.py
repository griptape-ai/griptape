from warpspeed.utils import TiktokenTokenizer


class TestTiktokenTokenizer:
    def test_encode(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.encode("foo bar") == [8134, 3703]

    def test_decode(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.decode([8134, 3703]) == "foo bar"

    def test_token_count(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.token_count("foo bar huzzah") == 5

    def test_tokens_left(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.tokens_left("foo bar huzzah") == 4083

    def test_encoding(self):
        tokenizer = TiktokenTokenizer()

        assert tokenizer.encoding.name == "cl100k_base"
