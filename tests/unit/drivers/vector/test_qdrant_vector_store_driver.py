import pytest
from griptape.drivers import QdrantVectorStoreDriver
from griptape.drivers import HuggingFaceHubEmbeddingDriver
from griptape.artifacts import TextArtifact


embedding_driver = HuggingFaceHubEmbeddingDriver(
       api_token='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', model='sentence-transformers/all-MiniLM-L6-v2')

class TestQdrantVectorVectorStoreDriver:
    @pytest.fixture(autouse=True)
    def mock_qdrant(self, mocker):
        # Mock the Qdrant search response
        fake_search_response = [{"id": "foo", "vector": [0, 1, 0], "score": 42, "payload": {"foo": "bar"}}]
        mocker.patch("qdrant_client.http.models.SearchRequest", return_value=fake_search_response)

    @pytest.fixture
    def driver(self):
        return QdrantVectorStoreDriver(
            url="http://localhost:6333",
            collection_name="test_1",
            embedding_driver=embedding_driver,
            )

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector(embedding_driver.try_embed_chunk("foo"), vector_id=1) == 1


    def test_upsert_text(self, driver):
        assert driver.upsert_text("foo",  vector_id=2) == 2


    def test_query(self, driver):
        results = driver.query("test",count=10)
