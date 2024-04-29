import pytest
from griptape.artifacts import TextArtifact


class TestGriptapeCloudStructureRunClient:
    @pytest.fixture
    def client(self, mocker):
        from griptape.tools import GriptapeCloudStructureRunClient

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"structure_run_id": 1}
        mocker.patch("requests.post", return_value=mock_response)

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"description": "fizz buzz", "output": "fooey booey", "status": "SUCCEEDED"}
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudStructureRunClient(base_url="https://api.griptape.ai", api_key="foo bar", structure_id="1")

    def test_execute_structure_run(self, client):
        assert isinstance(client.execute_structure_run({"values": {"args": ["foo bar"]}}), TextArtifact)

    def test_get_structure_description(self, client):
        assert client._get_structure_description() == "fizz buzz"

        client.description = "foo bar"
        assert client._get_structure_description() == "foo bar"
