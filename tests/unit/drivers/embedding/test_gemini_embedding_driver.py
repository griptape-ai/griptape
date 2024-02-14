from unittest.mock import Mock
import pytest
from griptape.drivers import GeminiEmbeddingDriver

class TestGeminiEmbeddingDriver:
    @pytest.fixture()
    def mock_client(self, mocker):
        mock_response = Mock()
        mock_response.values = [0, 1, 0]
        mock_instance = mocker.patch("vertexai.language_models.TextEmbeddingModel")
        mock_instance.return_value.get_embeddings.return_value = [mock_response]

        return mock_instance

    def test_init(self, mock_client):
        assert GeminiEmbeddingDriver(client=mock_client())

    def test_try_embed_chunk(self, mock_client):
        assert GeminiEmbeddingDriver(client=mock_client()).try_embed_chunk("foobar") == [0, 1, 0]
