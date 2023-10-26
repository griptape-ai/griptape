import pytest
from griptape.artifacts import TextArtifact
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from unittest.mock import patch


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

    @patch.object(MockEmbeddingDriver, "try_embed_string")
    def test_embed_string_throws_when_retries_exhausted(
        self, try_embed_string, driver
    ):
        try_embed_string.side_effect = Exception("nope")

        with pytest.raises(Exception) as e:
            driver.embed_string("foobar")

        assert e.value.args[0] == "nope"
