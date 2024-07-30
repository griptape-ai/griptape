from unittest.mock import Mock

import pytest

from griptape.drivers import VoyageAiEmbeddingDriver


class TestVoyageAiEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("voyageai.Client")
        mock_client.return_value.embed.return_value = Mock(embeddings=[[0, 1, 0]])

        return mock_client

    def test_init(self):
        assert VoyageAiEmbeddingDriver()

    def test_try_embed_chunk(self):
        assert VoyageAiEmbeddingDriver().try_embed_chunk("foobar") == [0, 1, 0]
