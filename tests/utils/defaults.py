from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


def text_tool_memory(name):
    return TextToolMemory(
        name=name,
        query_engine=VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        ),
        summary_engine=PromptSummaryEngine(),
        csv_extraction_engine=CsvExtractionEngine(),
        json_extraction_engine=JsonExtractionEngine()
    )
