from griptape.artifacts import TextArtifact
from griptape.common import Reference
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestVectorStoreRetrievalRagModule:
    def test_run_without_namespace(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        module = VectorStoreRetrievalRagModule(vector_store_driver=vector_store_driver)

        vector_store_driver.upsert_text_artifact(TextArtifact("foobar1", reference=Reference(title="boo")), namespace="test")
        vector_store_driver.upsert_text_artifact(TextArtifact("foobar2"), namespace="test")

        result = module.run(RagContext(query="test"))

        assert len(result) == 2
        assert result[0].value == "foobar1"
        assert result[1].value == "foobar2"

    def test_run_with_namespace(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        module = VectorStoreRetrievalRagModule(
            vector_store_driver=vector_store_driver, query_params={"namespace": "test"}
        )

        vector_store_driver.upsert_text_artifact(TextArtifact("foobar1"), namespace="test")
        vector_store_driver.upsert_text_artifact(TextArtifact("foobar2"), namespace="test")

        result = module.run(RagContext(query="test"))

        assert len(result) == 2
        assert result[0].value == "foobar1"
        assert result[1].value == "foobar2"

    def test_run_with_namespace_overrides(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        module = VectorStoreRetrievalRagModule(
            vector_store_driver=vector_store_driver, query_params={"namespace": "test"}
        )

        vector_store_driver.upsert_text_artifact(TextArtifact("foobar1"), namespace="test")
        vector_store_driver.upsert_text_artifact(TextArtifact("foobar2"), namespace="test")

        result1 = module.run(
            RagContext(
                query="test", module_configs={"VectorStoreRetrievalRagModule": {"query_params": {"namespace": "empty"}}}
            )
        )

        result2 = module.run(
            RagContext(
                query="test", module_configs={"VectorStoreRetrievalRagModule": {"query_params": {"namespace": "test"}}}
            )
        )

        assert len(result1) == 0
        assert len(result2) == 2
