class TestEmbeddings:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/embeddings/
    """

    def test_embeddings(self):
        from griptape.drivers import OpenAiEmbeddingDriver

        result = OpenAiEmbeddingDriver().embed_string("Hello Griptape!")

        assert isinstance(result, list)
