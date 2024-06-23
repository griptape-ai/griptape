import pytest
from unittest.mock import MagicMock, patch
from griptape.drivers import QdrantVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.utils import import_optional_dependency


class TestQdrantVectorVectorStoreDriver:
    @pytest.fixture
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture(autouse=True)
    def driver(self, mocker):
        # Mock the QdrantVectorStoreDriver class
        qdrant_mock = mocker.patch("griptape.drivers.QdrantVectorStoreDriver")
        qdrant_instance = qdrant_mock.return_value
        qdrant_instance.upsert_vector.return_value = "foo"
        qdrant_instance.upsert_text.return_value = 2
        qdrant_instance.query.return_value = [
            {"id": "foo", "vector": [0, 1, 0], "score": 42, "payload": {"foo": "bar"}}
        ]
        # Mock the response from the client.retrieve method for load_entry
        mock_entry = MagicMock()
        mock_entry.id = "foo"
        mock_entry.vector = [0.1, 0.2, 0.3]
        mock_entry.payload = {"meta_key": "meta_value"}
        qdrant_instance.load_entry.side_effect = [mock_entry, None]

        # Mock the response from the client.retrieve method for load_entries
        mock_entries = [MagicMock(id="foo", vector=[0.1, 0.2, 0.3], payload={"meta_key": "meta_value"})]
        qdrant_instance.load_entries.return_value = mock_entries

        return qdrant_instance

    @patch("griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency")
    def test_client_initialization(self, mock_import_optional_dependency, embedding_driver):
        # Mock the import_optional_dependency function to return a MagicMock
        mock_qdrant_client = MagicMock()
        mock_import_optional_dependency.return_value = mock_qdrant_client

        driver = QdrantVectorStoreDriver(
            location="/some/path",
            url="http://some_url",
            host="localhost",
            path=None,
            port=8080,
            grpc_port=50051,
            prefer_grpc=True,
            api_key=None,
            https=False,
            prefix=None,
            force_disable_check_same_thread=False,
            timeout=5,
            distance="COSINE",
            collection_name="some_collection",
            vector_name=None,
            content_payload_key="data",
            embedding_driver=embedding_driver,
        )

        mock_import_optional_dependency.assert_called_with("qdrant_client")
        mock_qdrant_client.QdrantClient.assert_called_with(
            location="/some/path",
            url="http://some_url",
            host="localhost",
            path=None,
            port=8080,
            grpc_port=50051,
            prefer_grpc=True,
            api_key=None,
            https=False,
            prefix=None,
            force_disable_check_same_thread=False,
            timeout=5,
        )

    def test_upsert_vector(self, driver):
        vector = [0, 1, 2]
        vector_id = "foo"
        meta = {"meta_key": "meta_value"}
        content = "content_string"

        # Test when all parameters are provided
        assert driver.upsert_vector(vector=vector, vector_id=vector_id, meta=meta, content=content) == vector_id

        # Test when vector_id is None
        generated_id = driver.upsert_vector(vector=vector)
        assert isinstance(generated_id, str)

        # Test when meta is None
        new_generated_id = driver.upsert_vector(vector=vector, vector_id=vector_id)
        assert new_generated_id == vector_id

        # Test when content is provided without meta
        assert driver.upsert_vector(vector=vector, vector_id=vector_id, content=content) == vector_id

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
        with patch.object(driver.client, "delete") as mock_delete:
            mock_delete.return_value.status = import_optional_dependency(
                "qdrant_client.http.models"
            ).UpdateStatus.COMPLETED
            assert driver.delete_vector(vector_id="2")

    def test_load_entry(self, driver):
        with patch.object(driver.client, "retrieve") as mock_retrieve:
            # Mock the response from the client.retrieve method for load_entry
            mock_entry = MagicMock()
            mock_entry.id = "foo"
            mock_entry.vector = [0.1, 0.2, 0.3]
            mock_entry.payload = {"meta_key": "meta_value"}

            # Test with existing entry
            mock_retrieve.side_effect = [[mock_entry], []]
            entry = driver.load_entry(vector_id="foo")
            assert entry.id == "foo"
            assert entry.vector == [0.1, 0.2, 0.3]
            assert entry.payload == {"meta_key": "meta_value"}

            # Test with non-existing entry
            mock_retrieve.side_effect = [[], []]
            entry = driver.load_entry(vector_id="non_existent_id")
            assert entry is None

    def test_load_entries(self, driver):
        with patch.object(driver.client, "retrieve") as mock_retrieve:
            mock_entry = MagicMock()
            mock_entry.id = "foo"
            mock_entry.vector = [0.1, 0.2, 0.3]
            mock_entry.payload = {"meta_key": "meta_value"}

            mock_retrieve.return_value = [mock_entry]

            entries = driver.load_entries(ids=["foo"], with_payload=True, with_vectors=True)

            assert entries[0].id == "foo"
            assert entries[0].vector == [0.1, 0.2, 0.3]
            assert entries[0].payload == {"meta_key": "meta_value"}
