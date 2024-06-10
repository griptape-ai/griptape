from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.memory import TaskMemory
from griptape.memory.task.storage import TextArtifactStorage, BlobArtifactStorage
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


def text_tool_artifact_storage():
    vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

    return TextArtifactStorage(
        rag_engine=VectorQueryEngine(
            vector_store_driver=vector_store_driver,
            prompt_driver=MockPromptDriver(),
        ),
        vector_store_driver=vector_store_driver,
        summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver()),
        csv_extraction_engine=CsvExtractionEngine(prompt_driver=MockPromptDriver()),
        json_extraction_engine=JsonExtractionEngine(prompt_driver=MockPromptDriver()),
    )


def text_task_memory(name):
    return TaskMemory(
        name=name, artifact_storages={TextArtifact: text_tool_artifact_storage(), BlobArtifact: BlobArtifactStorage()}
    )
