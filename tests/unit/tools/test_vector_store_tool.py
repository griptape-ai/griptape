from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.tools import VectorStoreTool
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestVectorStoreTool:
    def test_search(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool = VectorStoreTool(description="Test", vector_store_driver=driver)

        driver.upsert_collection({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert {a.value for a in tool.search({"values": {"query": "test"}})} == {"foo", "bar"}

    def test_search_with_namespace(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool1 = VectorStoreTool(description="Test", vector_store_driver=driver, query_params={"namespace": "test"})
        tool2 = VectorStoreTool(description="Test", vector_store_driver=driver, query_params={"namespace": "test2"})

        driver.upsert_collection({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert len(tool1.search({"values": {"query": "test"}})) == 2
        assert len(tool2.search({"values": {"query": "test"}})) == 0

    def test_custom_process_query_output(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool1 = VectorStoreTool(
            description="Test",
            vector_store_driver=driver,
            process_query_output=lambda es: ListArtifact([e.vector for e in es]),
            query_params={"include_vectors": True},
        )

        driver.upsert_collection({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert tool1.search({"values": {"query": "test"}}).value == [[0, 1], [0, 1]]
