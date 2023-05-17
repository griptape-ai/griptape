import pytest
from griptape.artifacts import TextArtifact
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestBaseEmbeddingDriver:
    @pytest.fixture
    def driver(self):
        return MockEmbeddingDriver()

    def test_embed_text_artifact(self, driver):
        embedding = driver.embed_text_artifact(TextArtifact("foobar"))

        assert embedding == [0, 1]

    def test_embed_string(self, driver):
        embedding = driver.embed_string("foobar")

        assert embedding == [0, 1]
