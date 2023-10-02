from typing import Optional
from attr import define, field, Factory
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.memory.tool import ToolMemory
from griptape.mixins import ToolMemoryActivitiesMixin
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


@define
class MockToolMemoryProcessor(ToolMemoryActivitiesMixin):
    memory: ToolMemory = field(
        default=Factory(
            lambda: ToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver()
                    ),
                    prompt_driver=MockPromptDriver()
                ),
                summary_engine=PromptSummaryEngine(
                    prompt_driver=MockPromptDriver()
                ),
                csv_extraction_engine=CsvExtractionEngine(
                    prompt_driver=MockPromptDriver()
                ),
                json_extraction_engine=JsonExtractionEngine(
                    prompt_driver=MockPromptDriver()
                )
            )
        )
    )

    def find_input_memory(self, memory_name: str) -> Optional[ToolMemory]:
        return self.memory
