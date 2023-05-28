import pytest
from griptape.loaders import WebLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestPdfLoader:
    @pytest.fixture
    def loader(self):
        return WebLoader(
            embedding_driver=MockEmbeddingDriver(),
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        list_artifact = loader.load("https://github.com/griptape-ai/griptape-tools")

        assert len(list_artifact.value) == 135
        assert list_artifact.value[0].value.startswith("Griptape")
        assert list_artifact.value[0].embedding == [0, 1]
