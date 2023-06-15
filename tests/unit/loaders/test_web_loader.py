import pytest
from griptape import utils
from griptape.loaders import WebLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestWebLoader:
    @pytest.fixture
    def loader(self):
        return WebLoader(
            embedding_driver=MockEmbeddingDriver(),
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        artifacts = loader.load("https://github.com/griptape-ai/griptape-tools")

        assert len(artifacts) > 1
        assert "griptape" in artifacts[0].value.lower()
        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader):
        artifacts = loader.load_collection([
            "https://github.com/griptape-ai/griptape",
            "https://github.com/griptape-ai/griptape-tools"
        ])

        assert list(artifacts.keys()) == [
            utils.str_to_hash("https://github.com/griptape-ai/griptape"),
            utils.str_to_hash("https://github.com/griptape-ai/griptape-tools")
        ]
        assert "griptape" in [a.value for artifact_list in artifacts.values() for a in artifact_list][0].lower()
