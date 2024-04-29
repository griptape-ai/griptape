import pytest
from griptape.artifacts import TextArtifact


class TestGriptapeCloudStructureRunClient:
    @pytest.fixture
    def client(self, mocker):
        from griptape.tools import GriptapeCloudStructureRunClient

        mock_response = mocker.Mock()
        mock_response.text.return_value = "foo bar"
        mocker.patch("requests.post", return_value=mock_response)

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"description": "fizz buzz", "output": "fooey booey", "status": "SUCCEEDED"}
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudStructureRunClient(base_url="https://api.griptape.ai", api_key="foo bar", structure_id="1")

    def test_submit_structure_run(self, client):
        assert isinstance(client.submit_structure_run({"values": {"args": ["foo bar"]}}), TextArtifact)

    def test_get_structure_run_result(self, client):
        assert isinstance(client.get_structure_run_result({"values": {"structure_run_id": "1"}}), TextArtifact)

    def test_get_structure_description(self, client):
        assert client._get_structure_description() == "fizz buzz"

        client.description = "foo bar"
        assert client._get_structure_description() == "foo bar"
