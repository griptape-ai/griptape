from typing import TYPE_CHECKING
import pytest
import mongomock
from griptape.artifacts import TextArtifact
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
if TYPE_CHECKING:
    from griptape.drivers import MongoDbAtlasVectorStoreDriver


class TestMongoDbAtlasVectorStoreDriver:

    @pytest.fixture
    def driver(self, monkeypatch):
        def mock_mongo_client():
            return mongomock.MongoClient()

        monkeypatch.setattr('pymongo.MongoClient', mock_mongo_client)
        embedding_driver = MockEmbeddingDriver()
        return MongoDbAtlasVectorStoreDriver(
            embedding_driver=embedding_driver,
            connection_string="mongodb://mock_connection_string",
            database_name="mock_database_name",
            collection_name="mock_collection_name"
        )

    def test_upsert_vector(self, driver):
        vector = [0.5, 0.5, 0.5]
        vector_id_str = "some_random_string_id"  # generating a string id
        test_id = driver.upsert_vector(vector, vector_id=vector_id_str)
        assert test_id is not None

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")
        test_id = driver.upsert_text_artifact(artifact)
        assert test_id is not None

    def test_upsert_text(self, driver):
        text = "foo"
        vector_id_str = "foo"
        test_id = driver.upsert_text(text, vector_id=vector_id_str)
        assert test_id is not None

    @pytest.mark.xfail(reason="Vector search not supported in MongoDB")
    def test_query(self, driver):
        query = "test"
        result = driver.query(query)
        assert result is not None

    def test_load_entry(self, driver):
        vector_id_str = "123"
        vector = [0.5, 0.5, 0.5]
        driver.upsert_vector(vector, vector_id=vector_id_str)  # ensure the entry exists
        result = driver.load_entry(vector_id_str)
        assert result is not None

    def test_load_entries(self, driver):
        vector_id_str = "123"
        vector = [0.5, 0.5, 0.5]
        driver.upsert_vector(vector, vector_id=vector_id_str)  # ensure at least one entry exists
        results = driver.load_entries()
        assert results is not None and len(results) > 0
