import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import MongoDbAtlasVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from unittest.mock import MagicMock

class TestMongoDbAtlasVectorStoreDriver:
    @pytest.fixture
    def driver(self, mocker):
        # Mock the pymongo.MongoClient
        mock_mongo_client = mocker.patch('pymongo.MongoClient', autospec=True)
        mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value.insert_one.return_value = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value.find.return_value = [
            {"vector": [0.5, 0.5, 0.5], "_id": "123", "meta": {"foo": "bar"}}
        ]

        return MongoDbAtlasVectorStoreDriver(
            connection_string="mongodb+srv://test:test@cluster0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
            database_name="test",
            collection_name="test",
            embedding_driver=MockEmbeddingDriver()
        )

    def test_upsert_vector(self, driver):
        vector = [0.5, 0.5, 0.5]
        vector_id = "123"
        id = driver.upsert_vector(vector, vector_id=vector_id)
        assert id == vector_id
        driver.collection.insert_one.assert_called_once()

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")
        id = driver.upsert_text_artifact(artifact)
        assert id == artifact.id
        driver.collection.insert_one.assert_called_once()

    def test_upsert_text(self, driver):
        text = "foo"
        vector_id = "foo"
        id = driver.upsert_text(text, vector_id=vector_id)
        assert id == vector_id
        driver.collection.insert_one.assert_called_once()

    def test_query(self, driver):
        query = "test"
        result = driver.query(query)
        assert len(result) == 1
        assert result[0].vector == [0.5, 0.5, 0.5]
        assert result[0].score is None
        assert result[0].meta == {"foo": "bar"}
        driver.collection.find.assert_called_once()

    def test_load_entry(self, driver):
        vector_id = "123"
        result = driver.load_entry(vector_id)
        assert result.id == "123"
        assert result.vector == [0.5, 0.5, 0.5]
        assert result.meta == {"foo": "bar"}
        driver.collection.find.assert_called_once()

    def test_load_entries(self, driver):
        results = driver.load_entries()
        assert len(results) == 1
        assert results[0].id == "123"
        assert results[0].vector == [0.5, 0.5, 0.5]
        assert results[0].meta == {"foo": "bar"}
        driver.collection.find.assert_called_once()
