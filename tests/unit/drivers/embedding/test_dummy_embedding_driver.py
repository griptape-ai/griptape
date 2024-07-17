import pytest

from griptape.drivers import DummyEmbeddingDriver
from griptape.exceptions import DummyError


class TestDummyEmbeddingDriver:
    @pytest.fixture()
    def embedding_driver(self):
        return DummyEmbeddingDriver()

    def test_init(self, embedding_driver):
        assert embedding_driver

    def test_try_embed_chunk(self, embedding_driver):
        with pytest.raises(DummyError):
            embedding_driver.try_embed_chunk("prompt-stack")
