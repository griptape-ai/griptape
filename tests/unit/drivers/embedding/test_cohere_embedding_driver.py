from unittest.mock import Mock

import pytest

from griptape.drivers import CohereEmbeddingDriver


class TestCohereEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value

        mock_client.embed.return_value = Mock(embeddings=[[0, 1, 0]])

        return mock_client

    def test_init(self):
        assert CohereEmbeddingDriver(model="embed-english-v3.0", api_key="bar", input_type="search_document")

    def test_try_embed_chunk(self):
        assert CohereEmbeddingDriver(
            model="embed-english-v3.0", api_key="bar", input_type="search_document"
        ).try_embed_chunk("foobar") == [0, 1, 0]
