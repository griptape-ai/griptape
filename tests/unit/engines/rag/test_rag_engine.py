import pytest

from griptape.drivers import LocalVectorStoreDriver
from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestRagEngine:
    @pytest.fixture()
    def engine(self):
        return RagEngine(
            retrieval_stage=RetrievalRagStage(
                retrieval_modules=[
                    VectorStoreRetrievalRagModule(
                        vector_store_driver=LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
                    )
                ]
            ),
            response_stage=ResponseRagStage(response_module=PromptResponseRagModule(prompt_driver=MockPromptDriver())),
        )

    def test_module_name_uniqueness(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

        with pytest.raises(ValueError):
            RagEngine(
                retrieval_stage=RetrievalRagStage(
                    retrieval_modules=[
                        VectorStoreRetrievalRagModule(name="test", vector_store_driver=vector_store_driver),
                        VectorStoreRetrievalRagModule(name="test", vector_store_driver=vector_store_driver),
                    ]
                )
            )

        assert RagEngine(
            retrieval_stage=RetrievalRagStage(
                retrieval_modules=[
                    VectorStoreRetrievalRagModule(name="test1", vector_store_driver=vector_store_driver),
                    VectorStoreRetrievalRagModule(name="test2", vector_store_driver=vector_store_driver),
                ]
            )
        )

    def test_process_query(self, engine):
        assert engine.process_query("test").output.value == "mock output"

    def test_process(self, engine):
        assert engine.process(RagContext(query="test")).output.value == "mock output"
