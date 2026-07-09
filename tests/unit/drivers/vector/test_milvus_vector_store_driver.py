from unittest.mock import MagicMock

import pytest

from griptape.drivers.vector.milvus import MilvusVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestMilvusVectorStoreDriver:
    @pytest.fixture()
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture()
    def client(self):
        client = MagicMock()
        client.describe_collection.return_value = self._collection_description(vector_dim=2)

        return client

    @pytest.fixture()
    def driver(self, embedding_driver, client):
        return MilvusVectorStoreDriver(
            collection_name="test_collection",
            embedding_driver=embedding_driver,
            client=client,
        )

    def test_client_uses_default_uri(self, embedding_driver, mocker):
        pymilvus = MagicMock()
        mocker.patch("griptape.utils.import_optional_dependency", return_value=pymilvus)

        driver = MilvusVectorStoreDriver(collection_name="test_collection", embedding_driver=embedding_driver)

        assert driver.client == pymilvus.MilvusClient.return_value
        pymilvus.MilvusClient.assert_called_once_with(uri="./milvus.db")

    def test_client_uses_authentication_kwargs(self, embedding_driver, mocker):
        pymilvus = MagicMock()
        mocker.patch("griptape.utils.import_optional_dependency", return_value=pymilvus)

        driver = MilvusVectorStoreDriver(
            collection_name="test_collection",
            embedding_driver=embedding_driver,
            uri="https://example.milvus.io",
            token="token",
            db_name="db",
        )

        assert driver.client == pymilvus.MilvusClient.return_value
        pymilvus.MilvusClient.assert_called_once_with(
            uri="https://example.milvus.io",
            token="token",
            db_name="db",
        )

    def test_rejects_invalid_metric_type(self, embedding_driver):
        with pytest.raises(ValueError, match="metric_type must be one of"):
            MilvusVectorStoreDriver(
                collection_name="test_collection",
                embedding_driver=embedding_driver,
                metric_type="invalid",
            )

    def test_upsert_vector_creates_collection(self, driver, client):
        client.has_collection.return_value = False
        schema = MagicMock()
        index_params = MagicMock()
        client.create_schema.return_value = schema
        client.prepare_index_params.return_value = index_params

        vector_id = driver.upsert_vector([1.0, 0.0], vector_id="vector-id", namespace="docs", meta={"source": "guide"})

        assert vector_id == "vector-id"
        client.create_schema.assert_called_once_with(auto_id=False, enable_dynamic_field=True)
        index_params.add_index.assert_called_once_with(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )
        client.create_collection.assert_called_once_with(
            collection_name="test_collection",
            schema=schema,
            index_params=index_params,
        )
        client.upsert.assert_called_once_with(
            collection_name="test_collection",
            data=[
                {
                    "id": "vector-id",
                    "vector": [1.0, 0.0],
                    "text": "",
                    "namespace": "docs",
                    "metadata": {"source": "guide"},
                    "source": "guide",
                }
            ],
        )

    def test_upsert_vector_uses_content(self, driver, client):
        client.has_collection.return_value = True

        driver.upsert_vector([1.0, 0.0], content="content", meta={"artifact": "not json"})

        assert client.upsert.call_args.kwargs["data"][0]["text"] == "content"

    def test_upsert_vector_rejects_long_field_value(self, embedding_driver, client):
        driver = MilvusVectorStoreDriver(
            collection_name="test_collection",
            embedding_driver=embedding_driver,
            client=client,
            id_max_length=3,
        )

        with pytest.raises(ValueError, match="cannot exceed"):
            driver.upsert_vector([1.0, 0.0], vector_id="long")

    def test_setup_creates_collection_with_consistency_level(self, embedding_driver, client):
        client.has_collection.return_value = False
        schema = MagicMock()
        index_params = MagicMock()
        client.create_schema.return_value = schema
        client.prepare_index_params.return_value = index_params
        driver = MilvusVectorStoreDriver(
            collection_name="test_collection",
            embedding_driver=embedding_driver,
            client=client,
            consistency_level="Strong",
        )

        driver.setup(vector_dim=2)

        client.create_collection.assert_called_once_with(
            collection_name="test_collection",
            schema=schema,
            index_params=index_params,
            consistency_level="Strong",
        )

    def test_setup_requires_vector_dim_for_missing_collection(self, driver, client):
        client.has_collection.return_value = False

        with pytest.raises(ValueError, match="vector_dim is required"):
            driver.setup()

    def test_load_entry_returns_none_when_collection_is_missing(self, driver, client):
        client.has_collection.return_value = False

        assert driver.load_entry("vector-id") is None

    def test_load_entry(self, driver, client):
        client.has_collection.return_value = True
        client.query.return_value = [
            {"id": "vector-id", "vector": [1.0, 0.0], "namespace": "docs", "metadata": {"source": "guide"}}
        ]

        entry = driver.load_entry("vector-id", namespace="docs")

        client.query.assert_called_once_with(
            collection_name="test_collection",
            filter='id == "vector-id" and namespace == "docs"',
            output_fields=["id", "text", "namespace", "metadata", "vector"],
        )
        assert entry is not None
        assert entry.id == "vector-id"
        assert entry.vector == [1.0, 0.0]
        assert entry.namespace == "docs"
        assert entry.meta == {"source": "guide"}

    def test_load_entries_returns_empty_when_collection_is_missing(self, driver, client):
        client.has_collection.return_value = False

        assert driver.load_entries() == []

    def test_load_entries_without_namespace(self, driver, client):
        client.has_collection.return_value = True
        client.query.return_value = [
            {"id": "vector-id", "vector": [1.0, 0.0], "namespace": None, "metadata": {"source": "guide"}}
        ]

        entries = driver.load_entries()

        client.query.assert_called_once_with(
            collection_name="test_collection",
            filter="",
            output_fields=["id", "text", "namespace", "metadata", "vector"],
        )
        assert entries[0].id == "vector-id"

    def test_query_vector(self, driver, client):
        client.has_collection.return_value = True
        client.search.return_value = [
            [
                {
                    "id": "vector-id",
                    "distance": 0.0,
                    "entity": {
                        "id": "vector-id",
                        "vector": [1.0, 0.0],
                        "namespace": "docs",
                        "metadata": {"source": "guide"},
                    },
                }
            ]
        ]

        entries = driver.query_vector(
            [1.0, 0.0],
            count=1,
            namespace="docs",
            include_vectors=True,
            filter={"source": "guide"},
        )

        client.search.assert_called_once_with(
            collection_name="test_collection",
            data=[[1.0, 0.0]],
            filter='namespace == "docs" and source == "guide"',
            limit=1,
            output_fields=["id", "text", "namespace", "metadata", "vector"],
            anns_field="vector",
            search_params={"metric_type": "COSINE"},
        )
        assert entries[0].id == "vector-id"
        assert entries[0].score == 1.0
        assert entries[0].vector == [1.0, 0.0]
        assert entries[0].namespace == "docs"
        assert entries[0].meta == {"source": "guide"}

    def test_query_vector_rejects_non_dict_filter(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="Milvus filter must be a dictionary"):
            driver.query_vector([1.0, 0.0], filter="source == guide")

    def test_query_vector_rejects_unsafe_filter_field(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="Invalid Milvus filter field name"):
            driver.query_vector([1.0, 0.0], filter={"source || id": "guide"})

    def test_query_vector_escapes_filter_value(self, driver, client):
        client.has_collection.return_value = True
        client.search.return_value = [[]]

        driver.query_vector([1.0, 0.0], filter={"source": 'guide" or id == "other'})

        assert client.search.call_args.kwargs["filter"] == 'source == "guide\\" or id == \\"other"'

    def test_query_vector_rejects_unsupported_filter_value(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="Milvus filters only support"):
            driver.query_vector([1.0, 0.0], filter={"source": {"nested": "value"}})

    def test_query_vector_rejects_empty_filter_list(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="lists cannot be empty"):
            driver.query_vector([1.0, 0.0], filter={"source": []})

    def test_query_vector_rejects_unsupported_filter_list_value(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="lists can only contain"):
            driver.query_vector([1.0, 0.0], filter={"source": ["guide", {"nested": "value"}]})

    def test_query_vector_rejects_metadata_filter_field(self, driver, client):
        client.has_collection.return_value = True

        with pytest.raises(ValueError, match="filtering is not supported"):
            driver.query_vector([1.0, 0.0], filter={"metadata": "guide"})

    def test_delete_vector(self, driver, client):
        client.has_collection.return_value = True

        driver.delete_vector("vector-id")

        client.delete.assert_called_once_with(collection_name="test_collection", ids=["vector-id"])

    def test_delete_vector_ignores_missing_collection(self, driver, client):
        client.has_collection.return_value = False

        driver.delete_vector("vector-id")

        client.delete.assert_not_called()

    def test_existing_collection_dimension_mismatch(self, driver, client):
        client.has_collection.return_value = True
        client.describe_collection.return_value = self._collection_description(vector_dim=3)

        with pytest.raises(ValueError, match="vector dimension"):
            driver.upsert_vector([1.0, 0.0])

    def test_existing_collection_missing_required_field(self, driver, client):
        client.has_collection.return_value = True
        collection_description = self._collection_description(vector_dim=2)
        collection_description["fields"] = collection_description["fields"][:-1]
        client.describe_collection.return_value = collection_description

        with pytest.raises(ValueError, match="missing required fields"):
            driver.upsert_vector([1.0, 0.0])

    def test_existing_collection_incompatible_field_type(self, driver, client):
        from pymilvus import DataType

        client.has_collection.return_value = True
        collection_description = self._collection_description(vector_dim=2)
        collection_description["fields"][2]["type"] = DataType.JSON
        client.describe_collection.return_value = collection_description

        with pytest.raises(ValueError, match="incompatible type"):
            driver.upsert_vector([1.0, 0.0])

    def test_existing_collection_requires_primary_key(self, driver, client):
        client.has_collection.return_value = True
        collection_description = self._collection_description(vector_dim=2)
        collection_description["fields"][0]["is_primary"] = False
        client.describe_collection.return_value = collection_description

        with pytest.raises(ValueError, match="must be the primary key"):
            driver.upsert_vector([1.0, 0.0])

    def test_score_from_distance(self, embedding_driver, client):
        assert (
            MilvusVectorStoreDriver(
                collection_name="test_collection", embedding_driver=embedding_driver, client=client
            )._score_from_distance(None)
            is None
        )
        assert (
            MilvusVectorStoreDriver(
                collection_name="test_collection",
                embedding_driver=embedding_driver,
                client=client,
                metric_type="L2",
            )._score_from_distance(2.0)
            == -2.0
        )
        assert (
            MilvusVectorStoreDriver(
                collection_name="test_collection",
                embedding_driver=embedding_driver,
                client=client,
                metric_type="IP",
            )._score_from_distance(2.0)
            == 2.0
        )

    def test_text_from_invalid_artifact(self, driver):
        assert driver._text_from_meta({"artifact": "not json"}) == ""

    @staticmethod
    def _collection_description(vector_dim: int) -> dict:
        from pymilvus import DataType

        return {
            "fields": [
                {"name": "id", "type": DataType.VARCHAR, "is_primary": True, "params": {"max_length": 512}},
                {"name": "vector", "type": DataType.FLOAT_VECTOR, "params": {"dim": vector_dim}},
                {"name": "text", "type": DataType.VARCHAR, "params": {"max_length": 65535}},
                {"name": "namespace", "type": DataType.VARCHAR, "params": {"max_length": 512}},
                {"name": "metadata", "type": DataType.JSON, "params": {}},
            ]
        }
