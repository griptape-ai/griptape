from attrs import define, field, Factory
from griptape.drivers import BasePromptDriver, LocalVectorStoreDriver
from griptape.drivers import (
    AmazonBedrockPromptDriver,
    BedrockClaudePromptModelDriver,
    BedrockTitanPromptModelDriver,
    AmazonBedrockTitanEmbeddingDriver,
    AmazonBedrockImageGenerationDriver,
    BedrockTitanImageGenerationModelDriver,
    BaseImageGenerationDriver,
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
class AmazonBedrockStructureConfig(BaseStructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda: AmazonBedrockPromptDriver(
                model="anthropic.claude-v2", stream=False, prompt_model_driver=BedrockClaudePromptModelDriver()
            )
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda: AmazonBedrockImageGenerationDriver(
                model="amazon.titan-image-generator-v1",
                image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
            )
        ),
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
