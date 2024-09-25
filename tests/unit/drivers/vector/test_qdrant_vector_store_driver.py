import uuid
from unittest.mock import MagicMock, patch

import pytest

from griptape.drivers import QdrantVectorStoreDriver
from griptape.utils import import_optional_dependency
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestQdrantVectorStoreDriver:
    @pytest.fixture()
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture()
    def mock_engine(self):
        return MagicMock()

    @pytest.fixture(autouse=True)
    def driver(self, embedding_driver, mocker):
        mocker.patch("qdrant_client.QdrantClient")
        return QdrantVectorStoreDriver(
            url="http://some_url",
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

    def test_delete_vector(self, driver):
        vector_id = "test_vector_id"

        mock_deletion_response = MagicMock()
        mock_deletion_response.status = import_optional_dependency("qdrant_client.http.models").UpdateStatus.COMPLETED

        with patch.object(driver.client, "delete", return_value=mock_deletion_response) as mock_delete, patch(
            "griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency"
        ) as mock_import:
            mock_import.return_value.PointIdsList.return_value = MagicMock()
            mock_import.return_value.UpdateStatus = import_optional_dependency("qdrant_client.http.models").UpdateStatus

            driver.delete_vector(vector_id)

            mock_delete.assert_called_once_with(
                collection_name=driver.collection_name,
                points_selector=mock_import.return_value.PointIdsList(points=[vector_id]),
            )

    def test_query(self, driver):
        mock_query_result = [
            MagicMock(
                id="foo", vector=[0, 1, 0], score=42, payload={"foo": "bar", "_score": 0.99, "_tensor_facets": []}
            )
        ]

        with patch.object(
            driver.embedding_driver, "embed_string", return_value=[0.1, 0.2, 0.3]
        ) as mock_embed, patch.object(driver.client, "search", return_value=mock_query_result) as mock_search:
            query = "test"
            count = 10
            include_vectors = True

            results = driver.query(query, count=count, include_vectors=include_vectors)

            mock_embed.assert_called_once_with(query)
            mock_search.assert_called_once_with(
                collection_name=driver.collection_name, query_vector=[0.1, 0.2, 0.3], limit=count
            )

            assert len(results) == 1
            assert results[0].id == "foo"
            assert results[0].vector == [0, 1, 0] if include_vectors else []
            assert results[0].score == 42
            assert results[0].meta == {"foo": "bar"}

    def test_upsert_with_batch(self, driver):
        vector = [0.1, 0.2, 0.3]
        vector_id = str(uuid.uuid4())
        meta = {"meta_key": "meta_value"}

        with patch("griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency") as mock_import:
            mock_batch = MagicMock()
            mock_import.return_value.Batch.return_value = mock_batch
            mock_qdrant_client = MagicMock()
            driver.client = mock_qdrant_client

            result = driver.upsert_vector(vector=vector, vector_id=vector_id, meta=meta)

            mock_import.assert_called_once_with("qdrant_client.http.models")
            mock_import.return_value.Batch.assert_called_once_with(ids=[vector_id], vectors=[vector], payloads=[meta])
            driver.client.upsert.assert_called_once_with(collection_name=driver.collection_name, points=mock_batch)
            assert result == vector_id

    def test_load_entry(self, driver):
        vector_id = str(uuid.uuid4())
        mock_entry = MagicMock()
        mock_entry.id = vector_id
        mock_entry.vector = [0.1, 0.2, 0.3]
        mock_entry.payload = {"meta_key": "meta_value", "_score": 0.99, "_tensor_facets": []}

        with patch.object(driver.client, "retrieve", return_value=[mock_entry]):
            result = driver.load_entry(vector_id)

            driver.client.retrieve.assert_called_once_with(collection_name=driver.collection_name, ids=[vector_id])

            assert result.id == vector_id
            assert result.vector == [0.1, 0.2, 0.3]
            assert result.meta == {"meta_key": "meta_value"}

        with patch.object(driver.client, "retrieve", return_value=[]):
            result = driver.load_entry(vector_id)

            driver.client.retrieve.assert_called_with(collection_name=driver.collection_name, ids=[vector_id])
            assert result is None

    def test_load_entries(self, driver):
        mock_entries = [
            MagicMock(
                id="id1", vector=[0.1, 0.2, 0.3], payload={"key1": "value1", "_score": 0.99, "_tensor_facets": []}
            ),
            MagicMock(
                id="id2", vector=[0.4, 0.5, 0.6], payload={"key2": "value2", "_score": 0.88, "_tensor_facets": []}
            ),
        ]

        with patch.object(driver.client, "retrieve", return_value=mock_entries) as mock_retrieve:
            results = driver.load_entries(ids=["id1", "id2"], with_payload=True, with_vectors=True)

            mock_retrieve.assert_called_once_with(
                collection_name=driver.collection_name, ids=["id1", "id2"], with_payload=True, with_vectors=True
            )

            assert len(results) == 2
            assert results[0].id == "id1"
            assert results[0].vector == [0.1, 0.2, 0.3]
            assert results[0].meta == {"key1": "value1"}
            assert results[1].id == "id2"
            assert results[1].vector == [0.4, 0.5, 0.6]
            assert results[1].meta == {"key2": "value2"}
