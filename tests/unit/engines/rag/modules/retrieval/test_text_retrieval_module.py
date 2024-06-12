from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import TextRetrievalModule
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestTextRetrievalModule:
    def test_run(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        module = TextRetrievalModule(vector_store_driver=vector_store_driver)

        vector_store_driver.upsert_text_artifact(TextArtifact("foobar1"), namespace="test")
        vector_store_driver.upsert_text_artifact(TextArtifact("foobar2"), namespace="test")

        result = module.run(RagContext(initial_query="test"))

        assert len(result) == 2
        assert result[0].value == "foobar1"
        assert result[1].value == "foobar2"
