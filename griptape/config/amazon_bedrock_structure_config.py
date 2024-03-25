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
    AmazonBedrockImageGenerationDriver,
    AmazonBedrockImageQueryDriver,
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    BedrockClaudePromptModelDriver,
    BedrockClaudeImageQueryModelDriver,
    BedrockTitanImageGenerationModelDriver,
    LocalVectorStoreDriver,
)


@define()
class AmazonBedrockStructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(
            lambda: StructureGlobalDriversConfig(
                prompt_driver=AmazonBedrockPromptDriver(
                    model="anthropic.claude-3-sonnet-20240229-v1:0",
                    stream=False,
                    prompt_model_driver=BedrockClaudePromptModelDriver(),
                ),
                image_generation_driver=AmazonBedrockImageGenerationDriver(
                    model="amazon.titan-image-generator-v1",
                    image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
                ),
                image_query_driver=AmazonBedrockImageQueryDriver(
                    model="anthropic.claude-3-sonnet-20240229-v1:0",
                    image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
                ),
                embedding_driver=AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-text-v1"),
                vector_store_driver=LocalVectorStoreDriver(
                    embedding_driver=AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-text-v1")
                ),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda self: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=self.global_drivers.prompt_driver,
                    vector_store_driver=self.global_drivers.vector_store_driver,
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(prompt_driver=self.global_drivers.prompt_driver),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(prompt_driver=self.global_drivers.prompt_driver),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(prompt_driver=self.global_drivers.prompt_driver),
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
