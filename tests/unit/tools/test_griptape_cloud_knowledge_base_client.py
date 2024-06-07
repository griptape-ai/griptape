import pytest
from griptape.artifacts import TextArtifact


class TestGriptapeCloudKnowledgeBaseClient:
    @pytest.fixture
    def client(self, mocker):
        from griptape.tools import GriptapeCloudKnowledgeBaseClient

        mock_response = mocker.Mock()
        mock_response.text.return_value = "foo bar"
        mocker.patch("requests.post", return_value=mock_response)

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"description": "fizz buzz"}
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudKnowledgeBaseClient(
            base_url="https://api.griptape.ai", api_key="foo bar", knowledge_base_id="1"
        )

    @pytest.fixture
    def client_no_description(self, mocker):
        from griptape.tools import GriptapeCloudKnowledgeBaseClient

        mock_response = mocker.Mock()
        mock_response.json.return_value = {}
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudKnowledgeBaseClient(
            base_url="https://api.griptape.ai", api_key="foo bar", knowledge_base_id="1"
        )

    @pytest.fixture
    def client_kb_error(self, mocker):
        from griptape.tools import GriptapeCloudKnowledgeBaseClient

        mock_response = mocker.Mock()
        mock_response.json.return_value = {}
        mock_response.status_code = 404
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudKnowledgeBaseClient(
            base_url="https://api.griptape.ai", api_key="foo bar", knowledge_base_id="1"
        )

    def test_query(self, client):
        assert isinstance(client.query({"values": {"query": "foo bar"}}), TextArtifact)

    def test_get_knowledge_base_description(self, client):
        assert client._get_knowledge_base_description() == "fizz buzz"

        client.description = "foo bar"
        assert client._get_knowledge_base_description() == "foo bar"

    def test_get_knowledge_base_description_error(self, client_no_description):
        with pytest.raises(ValueError) as e:
            client_no_description._get_knowledge_base_description()

            assert (
                str(e)
                == f"No description found for Knowledge Base {client_no_description.knowledge_base_id}. Please set a description, or manually set the `GriptapeCloudKnowledgeBaseClient.description` attribute."
            )

    def test_get_knowledge_base_kb_error(self, client_kb_error):
        with pytest.raises(ValueError) as e:
            client_kb_error._get_knowledge_base_description()

            assert str(e) == f"Error accessing Knowledge Base {client_kb_error.knowledge_base_id}."
