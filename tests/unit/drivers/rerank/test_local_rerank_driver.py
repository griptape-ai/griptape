import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.local import LocalRerankDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestLocalRerankDriver:
    @pytest.fixture()
    def mock_embedding_driver(self):
        return MockEmbeddingDriver()

    def test_run(self, mock_embedding_driver):
        driver = LocalRerankDriver(embedding_driver=mock_embedding_driver)
        result = driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])

        assert len(result) == 2
