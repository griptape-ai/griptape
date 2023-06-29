import json

import pytest
from griptape import utils
from griptape.loaders import WebLoader

MAX_TOKENS = 50


class TestWebLoader:
    @pytest.fixture(autouse=True)
    def mock_trafilatura(self, mocker):
        fake_response = {
            "status": 200,
            "data": "foobar"
        }

        fake_extract = {
            "text": "foobar"
        }

        mocker.patch("trafilatura.fetch_url", return_value=fake_response)
        mocker.patch("trafilatura.extract", return_value=json.dumps(fake_extract))

    @pytest.fixture
    def loader(self):
        return WebLoader(
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        artifacts = loader.load("https://github.com/griptape-ai/griptape-tools")

        assert len(artifacts) >= 1
        assert "foobar" in artifacts[0].value.lower()

    def test_load_collection(self, loader):
        artifacts = loader.load_collection([
            "https://github.com/griptape-ai/griptape",
            "https://github.com/griptape-ai/griptape-tools"
        ])

        assert list(artifacts.keys()) == [
            utils.str_to_hash("https://github.com/griptape-ai/griptape"),
            utils.str_to_hash("https://github.com/griptape-ai/griptape-tools")
        ]
        assert "foobar" in [a.value for artifact_list in artifacts.values() for a in artifact_list][0].lower()
