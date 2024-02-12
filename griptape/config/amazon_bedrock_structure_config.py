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
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    BedrockClaudePromptModelDriver,
    BedrockTitanImageGenerationModelDriver,
    BedrockTitanPromptModelDriver,
    LocalVectorStoreDriver,
)


@define()
class AmazonBedrockStructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(
            lambda: StructureGlobalDriversConfig(
                prompt_driver=AmazonBedrockPromptDriver(
                    model="anthropic.claude-v2", stream=False, prompt_model_driver=BedrockClaudePromptModelDriver()
                ),
                image_generation_driver=AmazonBedrockImageGenerationDriver(
                    model="amazon.titan-image-generator-v1",
                    image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
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
            lambda: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=AmazonBedrockPromptDriver(
                        model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
                    ),
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-text-v1")
                    ),
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(
                        prompt_driver=AmazonBedrockPromptDriver(
                            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
                        )
                    ),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(
                        prompt_driver=AmazonBedrockPromptDriver(
                            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
                        )
                    ),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(
                    prompt_driver=AmazonBedrockPromptDriver(
                        model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
                    )
                ),
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
