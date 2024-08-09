import pytest

from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage


class TestRagEngine:
    @pytest.fixture()
    def engine(self):
        return RagEngine(
            retrieval_stage=RetrievalRagStage(retrieval_modules=[VectorStoreRetrievalRagModule()]),
            response_stage=ResponseRagStage(response_module=PromptResponseRagModule()),
        )

    def test_module_name_uniqueness(self):
        with pytest.raises(ValueError):
            RagEngine(
                retrieval_stage=RetrievalRagStage(
                    retrieval_modules=[
                        VectorStoreRetrievalRagModule(name="test"),
                        VectorStoreRetrievalRagModule(name="test"),
                    ]
                )
            )

        assert RagEngine(
            retrieval_stage=RetrievalRagStage(
                retrieval_modules=[
                    VectorStoreRetrievalRagModule(name="test1"),
                    VectorStoreRetrievalRagModule(name="test2"),
                ]
            )
        )

    def test_process_query(self, engine):
        assert engine.process_query("test").output.value == "mock output"

    def test_process(self, engine):
        assert engine.process(RagContext(query="test")).output.value == "mock output"
