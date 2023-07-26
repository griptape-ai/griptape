import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import MongoDbAtlasVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from pymongo import MongoClient
from bson.objectid import ObjectId

class TestMongoDbAtlasVectorStoreDriver:
    @pytest.fixture
    def driver(self):
        # assuming you have these environment variables set
        # (they shouldn't be hardcoded for security reasons)
        connection_string = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority"
        return MongoDbAtlasVectorStoreDriver(
            connection_string=connection_string,
            database_name="test_db",
            collection_name="test_collection",
            embedding_driver=MockEmbeddingDriver(),
        )

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")
        vector_id = driver.upsert_text_artifact(artifact)
        assert vector_id == artifact.id

        # verify it exists in the database
        client = MongoClient(driver.connection_string)
        doc = client[driver.database_name][driver.collection_name].find_one({'_id': ObjectId(vector_id)})
        assert doc is not None
        assert doc['artifact'] == artifact.to_json()

    def test_upsert_vector(self, driver):
        vector_id = driver.upsert_vector([0, 1, 2], vector_id="foo")
        assert vector_id == "foo"

        # verify it exists in the database
        client = MongoClient(driver.connection_string)
        doc = client[driver.database_name][driver.collection_name].find_one({'_id': ObjectId(vector_id)})
        assert doc is not None
        assert doc['vector'] == [0, 1, 2]

    def test_upsert_text(self, driver):
        vector_id = driver.upsert_text("foo", vector_id="foo")
        assert vector_id == "foo"

        # verify it exists in the database
        client = MongoClient(driver.connection_string)
        doc = client[driver.database_name][driver.collection_name].find_one({'_id': ObjectId(vector_id)})
        assert doc is not None
        assert doc['Description'] == "foo"

    def test_load_entry(self, driver):
        vector_id = driver.upsert_text("foo", vector_id="foo")
        entry = driver.load_entry(vector_id)
        assert entry.id == vector_id
        assert entry.vector == [0, 1, 2]
        assert entry.meta['Description'] == "foo"

    def test_load_entries(self, driver):
        driver.upsert_text("foo", vector_id="foo")
        driver.upsert_text("bar", vector_id="bar")
        entries = driver.load_entries()
        assert len(entries) == 2
        ids = [entry.id for entry in entries]
        assert "foo" in ids
        assert "bar" in ids
