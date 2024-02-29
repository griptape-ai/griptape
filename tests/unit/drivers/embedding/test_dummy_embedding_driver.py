from griptape.drivers import DummyEmbeddingDriver
import pytest

from griptape.exceptions import DummyException


class TestDummyEmbeddingDriver:
    @pytest.fixture
    def embedding_driver(self):
        return DummyEmbeddingDriver()

    def test_init(self, embedding_driver):
        assert embedding_driver

    def test_try_embed_chunk(self, embedding_driver):
        with pytest.raises(DummyException):
            embedding_driver.try_embed_chunk("prompt-stack")
