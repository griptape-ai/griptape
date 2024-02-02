from griptape.drivers import NopEmbeddingDriver
import pytest

from griptape.exceptions import NopException


class TestNopEmbeddingDriver:
    @pytest.fixture
    def embedding_driver(self):
        return NopEmbeddingDriver()

    def test_init(self, embedding_driver):
        assert embedding_driver

    def test_try_embed_chunk(self, embedding_driver):
        with pytest.raises(NopException):
            embedding_driver.try_embed_chunk("prompt-stack")
