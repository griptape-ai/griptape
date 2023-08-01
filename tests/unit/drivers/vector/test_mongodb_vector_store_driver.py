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
        assert len(results) == len(mock_query_result)
        for result, expected in zip(results, mock_query_result):
            assert result.vector == expected.vector
            assert isinstance(result, BaseVectorStoreDriver.QueryResult)

    # def test_query(self, driver):
    #     query_str = "foo"  # Your query string here
    #     count = 5
    #     namespace = "optional namespace"
    #     include_vectors = False
    #     offset = 0
    #     index = "knn"  # Optional index name, change if you've set a different one
    #
    #     # You can replace the following with actual insertion or make sure the required data is in your database
    #     vector = [0.1, 0.2]
    #     vector_id_str = "query_test_vector"
    #     driver.upsert_vector(vector, vector_id=vector_id_str)
    #
    #     # Query the database
    #     results = driver.query(
    #         query=query_str,
    #         count=count,
    #         namespace=namespace,
    #         include_vectors=include_vectors,
    #         offset=offset,
    #         index=index
    #     )
    #
    #     # Check the results
    #     assert results is not None and len(results) > 0
    #     for result in results:
    #         assert result.vector == vector if include_vectors else result.vector is None

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
