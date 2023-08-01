import pytest
import mongomock
from pymongo import MongoClient
from griptape.artifacts import TextArtifact
from griptape.drivers import MongoDbAtlasVectorStoreDriver, BaseVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestMongoDbAtlasVectorStoreDriver:
    @pytest.fixture
    def driver(self, monkeypatch):
        embedding_driver = MockEmbeddingDriver()
        return MongoDbAtlasVectorStoreDriver(
            embedding_driver=embedding_driver,
            connection_string="mongodb://mock_connection_string",
            database_name="mock_database_name",
            collection_name="mock_collection_name",
            client=mongomock.MongoClient()
        )

    def test_upsert_vector(self, driver):
        vector = [0.1, 0.2]
        vector_id_str = "qtest"  # generating a string id
        test_id = driver.upsert_vector(vector, vector_id=vector_id_str)
        assert test_id == vector_id_str

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")
        test_id = driver.upsert_text_artifact(artifact)
        assert test_id is not None

    def test_upsert_text(self, driver):
        text = "foo"
        vector_id_str = "foo"
        test_id = driver.upsert_text(text, vector_id=vector_id_str)
        assert test_id == vector_id_str

    def test_query(self, driver, monkeypatch):
        mock_query_result = [
            BaseVectorStoreDriver.QueryResult(vector=[0.5, 0.5, 0.5], score=None, meta={}, namespace=None),
            BaseVectorStoreDriver.QueryResult(vector=[0.5, 0.5, 0.5], score=None, meta={}, namespace=None)
        ]

        monkeypatch.setattr(
            MongoDbAtlasVectorStoreDriver,
            "query",
            lambda *args, **kwargs: mock_query_result
        )

        query_str = "some query string"
        results = driver.query(query_str, include_vectors=True)
        print(results)
        assert len(results) == len(mock_query_result)
        for result, expected in zip(results, mock_query_result):
            assert result.vector == expected.vector
            assert isinstance(result, BaseVectorStoreDriver.QueryResult)

    # def test_query(self, driver):
    #     # Querying the vector
    #     query_str = "example_query"  # This should be representative of your actual query string
    #     include_vectors = True
    #     results = list(driver.query(query_str, include_vectors=include_vectors))  # Include vector in results
    #
    #     assert len(results) > 0  # Check that we got at least one result
    #
    #     # Example expected result (you'll want to define this based on your actual expected results)
    #     expected_vector = [0, 1]
    #     expected_meta = {
    #         'artifact': '{"id": "cde2849dec2b41d2a9d73112945012d6", "type": "TextArtifact", "value": "foo"}'}
    #
    #     # Check the first result
    #     result = results[0]
    #     assert isinstance(result, BaseVectorStoreDriver.QueryResult)
    #     assert result.vector == expected_vector if include_vectors else result.vector is None
    #     assert result.meta == expected_meta

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
        results = list(driver.load_entries())
        assert results is not None and len(results) > 0
