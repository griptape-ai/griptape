import pytest
from griptape.artifacts import TextArtifact


class TestGriptapeCloudKnowledgeBaseClient:
    @pytest.fixture
    def client(self, mocker):
        from griptape.tools import GriptapeCloudKnowledgeBaseClient

        mock_response = mocker.Mock()
        mock_response.text.return_value = "foo bar"
        mocker.patch("requests.post", return_value=mock_response)

        return GriptapeCloudKnowledgeBaseClient(
            base_url="https://api.griptape.ai", description="foo bar", api_key="foo bar", knowledge_base_id="1"
        )

    def test_query(self, client):
        assert isinstance(client.query({"values": {"query": "foo bar"}}), TextArtifact)
