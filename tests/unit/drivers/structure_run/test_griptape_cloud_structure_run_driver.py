import pytest

from griptape.artifacts import InfoArtifact, TextArtifact


class TestGriptapeCloudStructureRunDriver:
    @pytest.fixture()
    def driver(self, mocker):
        from griptape.drivers import GriptapeCloudStructureRunDriver

        mock_response = mocker.Mock()
        mock_response.json.return_value = {"structure_run_id": 1}
        mocker.patch("requests.post", return_value=mock_response)

        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "description": "fizz buzz",
            "output": TextArtifact("foo bar").to_dict(),
            "status": "SUCCEEDED",
        }
        mocker.patch("requests.get", return_value=mock_response)

        return GriptapeCloudStructureRunDriver(
            base_url="https://cloud-foo.griptape.ai", api_key="foo bar", structure_id="1", env={"key": "value"}
        )

    def test_run(self, driver):
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, TextArtifact)
        assert result.value == "foo bar"

    def test_async_run(self, driver):
        driver.async_run = True
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, InfoArtifact)
        assert result.value == "Run started successfully"
