import pytest

from griptape.artifacts import InfoArtifact, TextArtifact


class TestGriptapeCloudStructureRunDriver:
    @pytest.fixture()
    def mock_requests_post(self, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"structure_run_id": 1}
        return mocker.patch("requests.post", return_value=mock_response)

    @pytest.fixture()
    def driver(self, mocker, mock_requests_post):
        from griptape.drivers import GriptapeCloudStructureRunDriver

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

    def test_run(self, driver, mock_requests_post):
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, TextArtifact)
        assert result.value == "foo bar"
        mock_requests_post.assert_called_once_with(
            "https://cloud-foo.griptape.ai/api/structures/1/runs",
            json={"args": ["foo bar"], "env_vars": [{"name": "key", "value": "value", "source": "manual"}]},
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_async_run(self, driver):
        driver.async_run = True
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, InfoArtifact)
        assert result.value == "Run started successfully"
