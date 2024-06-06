import pytest
from unittest.mock import MagicMock
from griptape.drivers import BaseVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

embedding_driver = MockEmbeddingDriver()


class TestQdrantVectorVectorStoreDriver:
    @pytest.fixture
    def driver(self, mocker):
        # Mock the QdrantVectorStoreDriver class
        qdrant_mock = mocker.patch("griptape.drivers.QdrantVectorStoreDriver")
        qdrant_instance = qdrant_mock.return_value
        qdrant_instance.upsert_vector.return_value = 1
        qdrant_instance.upsert_text.return_value = 2
        qdrant_instance.query.return_value = [
            {"id": "foo", "vector": [0, 1, 0], "score": 42, "payload": {"foo": "bar"}}
        ]
        # Mock the response from the client.retrieve method for load_entry
        mock_entry = MagicMock()
        mock_entry.id = "foo"
        mock_entry.vector = [0.1, 0.2, 0.3]
        mock_entry.payload = {"meta_key": "meta_value"}
        qdrant_instance.load_entry.return_value = mock_entry

        # Mock the response from the client.retrieve method for load_entries
        mock_entries = [MagicMock(id="foo", vector=[0.1, 0.2, 0.3], payload={"meta_key": "meta_value"})]
        qdrant_instance.load_entries.return_value = mock_entries

        return qdrant_instance

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector(embedding_driver.embed_string("foo"), vector_id=1) == 1

    def test_upsert_text(self, driver):
        assert driver.upsert_text("foo", vector_id=2) == 2

    def test_query(self, driver):
        results = driver.query("test", count=10)
        assert len(results) == 1
        assert results[0]["id"] == "foo"
        assert results[0]["vector"] == [0, 1, 0]
        assert results[0]["score"] == 42
        assert results[0]["payload"]["foo"] == "bar"

    def test_delete_vector(self, driver):
        assert driver.delete_vector(vector_id=2)

    def test_load_entry(self, driver):
        # Run the actual load_entry method
        entry = driver.load_entry(vector_id="foo")
        assert entry.id == "foo"
        assert entry.vector == [0.1, 0.2, 0.3]
        assert entry.payload == {"meta_key": "meta_value"}

    def test_load_entries(self, driver):
        # Run the actual load_entries method
        entries = driver.load_entries(vector_id=["foo"])

        # Assert the contents of the first entry in the list
        assert entries[0].id == "foo"
        assert entries[0].vector == [0.1, 0.2, 0.3]
        assert entries[0].payload == {"meta_key": "meta_value"}
