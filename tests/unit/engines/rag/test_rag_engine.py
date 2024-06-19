import pytest
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines.rag import RagEngine, RagContext
from griptape.engines.rag.modules import TextRetrievalRagModule, PromptGenerationRagModule
from griptape.engines.rag.stages import RetrievalStage, GenerationStage
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestRagEngine:
    @pytest.fixture
    def engine(self):
        return RagEngine(
            retrieval_stage=RetrievalStage(
                retrieval_modules=[
                    TextRetrievalRagModule(
                        vector_store_driver=LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
                    )
                ]
            ),
            generation_stage=GenerationStage(
                generation_module=PromptGenerationRagModule(prompt_driver=MockPromptDriver())
            ),
        )

    def test_process_query(self, engine):
        assert engine.process_query("test").output.value == "mock output"

    def test_process(self, engine):
        assert engine.process(RagContext(initial_query="test")).output.value == "mock output"
