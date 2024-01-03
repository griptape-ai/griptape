from attrs import define, field, Factory
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver, LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.config import (
    StructureConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
)


@define(kw_only=True)
class OpenAiStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model="gpt-4", stream=False)), kw_only=True
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k"),
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-ada-002")
                    ),
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(
                        prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k")
                    ),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(
                        prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k")
                    ),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k")
                ),
            )
        ),
        kw_only=True,
    )
