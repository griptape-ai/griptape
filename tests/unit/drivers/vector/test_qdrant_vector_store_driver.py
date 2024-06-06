import pytest
from unittest.mock import MagicMock, patch
from griptape.drivers import QdrantVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.utils import import_optional_dependency


class TestQdrantVectorVectorStoreDriver:
    @pytest.fixture
    def embedding_driver(self):
        return MockEmbeddingDriver()

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

    def test_upsert_vector(self, driver, embedding_driver):
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

    from unittest.mock import patch

    def test_delete_vector(self, driver):
        with patch.object(driver.client, "delete") as mock_delete:
            mock_delete.return_value.status = import_optional_dependency(
                "qdrant_client.http.models"
            ).UpdateStatus.COMPLETED
            assert driver.delete_vector(vector_id="2")

    def test_load_entry(self, driver):
        entry = driver.load_entry(vector_id="foo")

        assert entry.id == "foo"
        assert entry.vector == [0.1, 0.2, 0.3]
        assert entry.payload == {"meta_key": "meta_value"}

    def test_load_entries(self, driver):
        entries = driver.load_entries(vector_id=["foo"])

        assert entries[0].id == "foo"
        assert entries[0].vector == [0.1, 0.2, 0.3]
        assert entries[0].payload == {"meta_key": "meta_value"}

    @patch("griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency")
    def test_client_initialization_in_memory(self, mock_import_optional_dependency, embedding_driver):
        mock_qdrant_client = MagicMock()
        mock_import_optional_dependency.return_value = mock_qdrant_client

        driver = QdrantVectorStoreDriver(
            location=":memory:",
            url="some_url",
            host="localhost",
            port=8080,
            prefer_grpc=True,
            grpc_port=50051,
            embedding_driver=embedding_driver,
            collection_name="some_collection",
        )

        mock_import_optional_dependency.assert_called_with("qdrant_client")
        mock_qdrant_client.AsyncQdrantClient.assert_called_with(
            location=":memory:", url="some_url", host="localhost", port=8080, prefer_grpc=True, grpc_port=50051
        )

    @patch("griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency")
    def test_client_initialization_not_in_memory(self, mock_import_optional_dependency, embedding_driver):
        # Mock the import_optional_dependency function to return a MagicMock
        mock_qdrant_client = MagicMock()
        mock_import_optional_dependency.return_value = mock_qdrant_client

        driver = QdrantVectorStoreDriver(
            location="/some/path",
            url="some_url",
            host="localhost",
            port=8080,
            prefer_grpc=True,
            grpc_port=50051,
            embedding_driver=embedding_driver,
            collection_name="some_collection",
        )

        mock_import_optional_dependency.assert_called_with("qdrant_client")
        mock_qdrant_client.QdrantClient.assert_called_with(
            location="/some/path", url="some_url", host="localhost", port=8080, prefer_grpc=True, grpc_port=50051
        )
