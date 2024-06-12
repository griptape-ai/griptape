from unittest.mock import Mock
import pytest
from griptape.drivers import CohereRerankDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import TextRerankModule


class TestTextRerankModule:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_client.rerank.return_value.results = [Mock(), Mock()]

        return mock_client

    def test_run(self, mock_client):
        module = TextRerankModule(rerank_driver=CohereRerankDriver(api_key="api-key"))
        result = module.run(RagContext(initial_query="test"))

        assert len(result) == 2
