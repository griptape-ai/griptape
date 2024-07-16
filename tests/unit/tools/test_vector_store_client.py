import pytest

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.tools import VectorStoreClient
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestVectorStoreClient:
    @pytest.fixture(autouse=True)
    def _mock_try_run(self, mocker):
        mocker.patch("griptape.drivers.OpenAiEmbeddingDriver.try_embed_chunk", return_value=[0, 1])

    def test_search(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool = VectorStoreClient(description="Test", vector_store_driver=driver)

        driver.upsert_text_artifacts({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert {a.value for a in tool.search({"values": {"query": "test"}})} == {"foo", "bar"}

    def test_search_with_namespace(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool1 = VectorStoreClient(description="Test", vector_store_driver=driver, query_params={"namespace": "test"})
        tool2 = VectorStoreClient(description="Test", vector_store_driver=driver, query_params={"namespace": "test2"})

        driver.upsert_text_artifacts({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert len(tool1.search({"values": {"query": "test"}})) == 2
        assert len(tool2.search({"values": {"query": "test"}})) == 0

    def test_custom_process_query_output_fn(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool1 = VectorStoreClient(
            description="Test",
            vector_store_driver=driver,
            process_query_output_fn=lambda es: ListArtifact([e.vector for e in es]),
            query_params={"include_vectors": True},
        )

        driver.upsert_text_artifacts({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert tool1.search({"values": {"query": "test"}}).value == [[0, 1], [0, 1]]
