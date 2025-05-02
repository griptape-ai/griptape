import pytest
import requests

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.nvidia_nim import NvidiaNimRerankDriver


class TestNvidiaNimRerankDriver:
    @pytest.fixture()
    def mock_client(self, mocker):
        def mock_post(*args, **kwargs):
            return mocker.Mock(
                status_code=200,
                json=lambda: {
                    "rankings": [
                        {"index": 0, "logit": 0.1, "usage": {"prompt_tokens": 10, "total_tokens": 20}},
                        {"index": 1, "logit": 0.2, "usage": {"prompt_tokens": 10, "total_tokens": 20}},
                    ]
                },
            )

        mocker.patch("griptape.drivers.rerank.nvidia_nim_rerank_driver.requests.post", side_effect=mock_post)

    @pytest.fixture()
    def mock_empty_client(self, mocker):
        def mock_post(*args, **kwargs):
            return mocker.Mock(
                status_code=200,
                json=lambda: {"rankings": []},
            )

        mocker.patch("griptape.drivers.rerank.nvidia_nim_rerank_driver.requests.post", side_effect=mock_post)

    def test_run(self, mock_client):
        driver = NvidiaNimRerankDriver(model="model-name", base_url="http://localhost:8000")
        result = driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])

        assert len(result) == 2

    def test_run_empty_artifacts(self, mock_empty_client):
        driver = NvidiaNimRerankDriver(model="model-name", base_url="http://localhost:8000")
        result = driver.run("hello", artifacts=[TextArtifact(""), TextArtifact("  ")])

        assert len(result) == 0

        result = driver.run("hello", artifacts=[])
        assert len(result) == 0

    def test_run_error(self, mocker):
        mocker.patch(
            "griptape.drivers.rerank.nvidia_nim_rerank_driver.requests.post",
            return_value=mocker.Mock(
                status_code=500,
                text="Internal Server Error",
                raise_for_status=lambda: (_ for _ in ()).throw(requests.exceptions.HTTPError()),
            ),
        )

        driver = NvidiaNimRerankDriver(model="model-name", base_url="http://localhost:8000")

        with pytest.raises(requests.exceptions.HTTPError):
            driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])
