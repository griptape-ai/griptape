class TestChunkers:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/chunkers/
    """

    def test_chunkers(self):
        from griptape.chunkers import TextChunker
        from griptape.tokenizers import TiktokenTokenizer

        result = TextChunker(
            # set an optional custom tokenizer
            tokenizer=TiktokenTokenizer(),
            # optionally modify default number of tokens
            max_tokens=100,
        ).chunk("long text")

        assert result[0] is not None
        assert result[0].value == "long text"
