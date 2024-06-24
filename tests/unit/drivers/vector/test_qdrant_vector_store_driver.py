import pytest
from unittest.mock import MagicMock, patch
from griptape.drivers import QdrantVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.utils import import_optional_dependency


class TestQdrantVectorStoreDriver:
    @pytest.fixture
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture
    def mock_engine(self):
        return MagicMock()

    @pytest.fixture(autouse=True)
    def driver(self, embedding_driver):
        driver = QdrantVectorStoreDriver(
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
        return driver

    def test_attrs_post_init(self, driver):
        with patch("griptape.drivers.vector.qdrant_vector_store_driver.import_optional_dependency") as mock_import:
            mock_qdrant_client = MagicMock()
            mock_import.return_value.QdrantClient.return_value = mock_qdrant_client

            driver.__attrs_post_init__()

            mock_import.assert_called_once_with("qdrant_client")
            mock_import.return_value.QdrantClient.assert_called_once_with(
                location=driver.location,
                url=driver.url,
                host=driver.host,
                path=driver.path,
                port=driver.port,
                prefer_grpc=driver.prefer_grpc,
                grpc_port=driver.grpc_port,
                api_key=driver.api_key,
                https=driver.https,
                prefix=driver.prefix,
                force_disable_check_same_thread=driver.force_disable_check_same_thread,
                timeout=driver.timeout,
            )
            assert driver.client == mock_qdrant_client

    def test_upsert_vector(self, driver):
        vector = [0, 1, 2]
        vector_id = "foo"
        meta = {"meta_key": "meta_value"}
        content = "content_string"

        with patch.object(driver, "upsert_vector", return_value=vector_id):
            assert driver.upsert_vector(vector=vector, vector_id=vector_id, meta=meta, content=content) == vector_id
            assert driver.upsert_vector(vector=None, vector_id=vector_id, meta=None, content=None) == vector_id

    def test_query(self, driver):
        mock_query_result = [{"id": "foo", "vector": [0, 1, 0], "score": 42, "payload": {"foo": "bar"}}]

        with patch.object(driver, "query", return_value=mock_query_result):
            results = driver.query("test", count=10)
            assert len(results) == 1
            assert results[0]["id"] == "foo"
            assert results[0]["vector"] == [0, 1, 0]
            assert results[0]["score"] == 42
            assert results[0]["payload"]["foo"] == "bar"
