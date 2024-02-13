from attrs import define, field, Factory
from griptape.drivers import LocalVectorStoreDriver
from griptape.config import (
    BaseStructureConfig,
    StructureGlobalDriversConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
)
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


@define
class MockStructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(
            lambda: StructureGlobalDriversConfig(
                prompt_driver=MockPromptDriver(),
                image_generation_driver=MockImageGenerationDriver(model="dall-e-2"),
                image_query_driver=MockImageQueryDriver(model="gpt-4-vision-preview"),
                embedding_driver=MockEmbeddingDriver(model="text-embedding-ada-002"),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=MockPromptDriver(model="gpt-3.5-turbo"),
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver(model="text-embedding-ada-002")
                    ),
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(
                        prompt_driver=MockPromptDriver(model="gpt-3.5-turbo")
                    ),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(
                        prompt_driver=MockPromptDriver(model="gpt-3.5-turbo")
                    ),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(
                    prompt_driver=MockPromptDriver(model="gpt-3.5-turbo")
                ),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
