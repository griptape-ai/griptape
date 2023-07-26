import pytest
import mongomock
from griptape.artifacts import TextArtifact
from griptape.drivers import MongoDbAtlasVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

class TestMongoDbAtlasVectorStoreDriver:

    @pytest.fixture
    def driver(self, monkeypatch):
        monkeypatch.setattr('pymongo.MongoClient', mongomock.MongoClient)
        embedding_driver = MockEmbeddingDriver()
        return MongoDbAtlasVectorStoreDriver(embedding_driver=embedding_driver)

    def test_upsert_vector(self, driver):
        vector = [0.5, 0.5, 0.5]
        vector_id = "123"
        id = driver.upsert_vector(vector, vector_id=vector_id)
        assert id is not None

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")
        id = driver.upsert_text_artifact(artifact)
        assert id is not None

    def test_upsert_text(self, driver):
        text = "foo"
        vector_id = "foo"
        id = driver.upsert_text(text, vector_id=vector_id)
        assert id is not None

    def test_query(self, driver):
        query = "test"
        result = driver.query(query)
        assert result is not None

    def test_load_entry(self, driver):
        vector_id = "123"
        result = driver.load_entry(vector_id)
        assert result is not None

    def test_load_entries(self, driver):
        results = driver.load_entries()
        assert results is not None
