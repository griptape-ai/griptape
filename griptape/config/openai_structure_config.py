from attrs import define, field, Factory
from griptape.drivers import (
    BasePromptDriver,
    OpenAiChatPromptDriver,
    LocalVectorStoreDriver,
    OpenAiEmbeddingDriver,
    BaseImageGenerationDriver,
    OpenAiImageGenerationDriver,
    BaseConversationMemoryDriver,
    LocalConversationMemoryDriver,
)
from griptape.config import (
    BaseStructureConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
)


@define(kw_only=True)
class OpenAiStructureConfig(BaseStructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model="gpt-4", stream=False)),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(lambda: OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512")),
        kw_only=True,
        metadata={"serializable": True},
    )
    conversation_memory_driver: BaseConversationMemoryDriver = field(
        default=Factory(lambda: LocalConversationMemoryDriver()), kw_only=True, metadata={"serializable": True}
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
