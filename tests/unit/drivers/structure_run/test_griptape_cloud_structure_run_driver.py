import pytest
from griptape.artifacts import TextArtifact


class TestGriptapeCloudStructureRunDriver:
    @pytest.fixture
    def driver(self, mocker):
        from griptape.drivers import GriptapeCloudStructureRunDriver

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"structure_run_id": 1}
        mocker.patch("requests.post", return_value=mock_response)

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"description": "fizz buzz", "output": "fooey booey", "status": "SUCCEEDED"}
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudStructureRunDriver(base_url="https://api.griptape.ai", api_key="foo bar", structure_id="1")

    def test_run(self, driver):
        assert isinstance(driver.run("foo bar"), TextArtifact)
