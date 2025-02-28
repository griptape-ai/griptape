import pytest

from griptape.drivers.embedding.dummy import DummyEmbeddingDriver
from griptape.exceptions import DummyError


class TestDummyEmbeddingDriver:
    @pytest.fixture()
    def embedding_driver(self):
        return DummyEmbeddingDriver()

    def test_init(self, embedding_driver):
        assert embedding_driver

    def test_embed(self, embedding_driver):
        with pytest.raises(DummyError):
            embedding_driver.embed("prompt-stack")
