from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import TextRetrievalRagModule, PromptGenerationRagModule
from griptape.engines.rag.stages import RetrievalRagStage, GenerationRagStage
from griptape.memory import TaskMemory
from griptape.memory.task.storage import TextArtifactStorage, BlobArtifactStorage
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


def text_tool_artifact_storage():
    vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

    return TextArtifactStorage(
        rag_engine=rag_engine(MockPromptDriver(), vector_store_driver),
        vector_store_driver=vector_store_driver,
        summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver()),
        csv_extraction_engine=CsvExtractionEngine(prompt_driver=MockPromptDriver()),
        json_extraction_engine=JsonExtractionEngine(prompt_driver=MockPromptDriver()),
    )


def text_task_memory(name):
    return TaskMemory(
        name=name, artifact_storages={TextArtifact: text_tool_artifact_storage(), BlobArtifact: BlobArtifactStorage()}
    )


def rag_engine(prompt_driver, vector_store_driver):
    return RagEngine(
        retrieval_stage=RetrievalRagStage(
            retrieval_modules=[TextRetrievalRagModule(vector_store_driver=vector_store_driver)]
        ),
        generation_stage=GenerationRagStage(generation_module=PromptGenerationRagModule(prompt_driver=prompt_driver)),
    )
