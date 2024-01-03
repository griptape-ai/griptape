from attrs import define, field, Factory
from griptape.config import (
    StructureConfig,
    StructureTaskMemoryConfig,
    PromptDriverConfig,
    VectorStoreDriverConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
)


@define(kw_only=True)
class OpenAiStructureConfig(StructureConfig):
    prompt_driver: PromptDriverConfig = field(
        default=Factory(lambda: PromptDriverConfig({"type": "OpenAiChatPromptDriver", "model": "gpt-4"})), kw_only=True
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=PromptDriverConfig(), vector_store_driver=VectorStoreDriverConfig()
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(prompt_driver=PromptDriverConfig()),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(prompt_driver=PromptDriverConfig()),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(prompt_driver=PromptDriverConfig()),
            )
        ),
        kw_only=True,
    )
