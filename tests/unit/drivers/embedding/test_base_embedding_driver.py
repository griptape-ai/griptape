from unittest.mock import patch

import pytest

from griptape.artifacts import TextArtifact
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestBaseEmbeddingDriver:
    @pytest.fixture()
    def driver(self):
        return MockEmbeddingDriver()

    def test_embed_text_artifact(self, driver):
        embedding = driver.embed_text_artifact(TextArtifact("foobar"))

        assert embedding == [0, 1]

    def test_embed_string(self, driver):
        embedding = driver.embed_string("foobar")

        assert embedding == [0, 1]

    def test_embed_long_string(self, driver):
        embedding = driver.embed_string("foobar" * 5000)

        assert embedding == [0, 1]

    def test_no_tokenizer(self, driver):
        driver.tokenizer = None

        embedding = driver.embed_string("foobar")

        assert embedding == [0, 1]

    @patch.object(MockEmbeddingDriver, "try_embed_chunk")
    def test_embed_string_throws_when_retries_exhausted(self, try_embed_chunk, driver):
        try_embed_chunk.side_effect = Exception("nope")

        with pytest.raises(Exception) as e:
            driver.embed_string("foobar")

        assert e.value.args[0] == "nope"
