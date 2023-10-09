from griptape.drivers import LocalVectorStoreDriver, LocalBlobToolMemoryDriver
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.memory import ToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


def text_tool_memory(name):
    return ToolMemory(
        name=name,
        query_engine=VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        ),
        summary_engine=PromptSummaryEngine(),
        csv_extraction_engine=CsvExtractionEngine(),
        json_extraction_engine=JsonExtractionEngine(),
        blob_storage_driver=LocalBlobToolMemoryDriver()
    )
