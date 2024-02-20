from attrs import Factory, define, field

from griptape.config import (
    BaseStructureConfig,
    StructureGlobalDriversConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
)
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiVisionImageQueryDriver,
)


@define
class OpenAiStructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(
            lambda: StructureGlobalDriversConfig(
                prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
                image_generation_driver=OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512"),
                image_query_driver=OpenAiVisionImageQueryDriver(model="gpt-4-vision-preview", max_tokens=300),
                embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-ada-002"),
                vector_store_driver=LocalVectorStoreDriver(
                    embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-ada-002")
                ),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-ada-002")
                    ),
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(
                        prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo")
                    ),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(
                        prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo")
                    ),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo")
                ),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
