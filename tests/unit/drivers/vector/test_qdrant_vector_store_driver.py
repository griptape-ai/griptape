import pytest
from griptape.drivers import QdrantVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.artifacts import TextArtifact

embedding_driver = MockEmbeddingDriver()


class TestQdrantVectorVectorStoreDriver:

    @pytest.fixture
    def driver(self, mocker):
        # Mock the QdrantVectorStoreDriver class
        qdrant_mock = mocker.patch("griptape.drivers.QdrantVectorStoreDriver")
        qdrant_instance = qdrant_mock.return_value
        qdrant_instance.upsert_vector.return_value = 1
        qdrant_instance.upsert_text.return_value = 2
        qdrant_instance.query.return_value = [{"id": "foo", "vector": [0, 1, 0], "score": 42, "payload": {"foo": "bar"}}]
        return qdrant_instance

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector(embedding_driver.try_embed_chunk("foo"), vector_id=1) == 1

    def test_upsert_text(self, driver):
        assert driver.upsert_text("foo", vector_id=2) == 2

    def test_query(self, driver):
        results = driver.query("test", count=10)
