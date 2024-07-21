import pytest

from griptape.drivers import OllamaEmbeddingDriver


class TestOllamaEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("ollama.Client")

        mock_client.return_value.embeddings.return_value = {"embedding": [0, 1, 0]}

        return mock_client

    def test_init(self):
        assert OllamaEmbeddingDriver(model="foo")

    def test_try_embed_chunk(self):
        assert OllamaEmbeddingDriver(model="foo").try_embed_chunk("foobar") == [0, 1, 0]
