import pytest
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
            "02770953bca8c14e7602f7f1020551820f8ff105713f8d9522b0302755a9372a",
            "be0c50c506c5dd96e6b8dfe45f9eff0d5fe99411565aed3e1682b230e0f44922"
        ]
        assert "griptape" in [a.value for artifact_list in artifacts.values() for a in artifact_list][0].lower()
