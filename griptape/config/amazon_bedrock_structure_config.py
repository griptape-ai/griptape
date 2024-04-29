from attrs import define, field, Factory

from griptape.config import StructureConfig
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
class AmazonBedrockStructureConfig(StructureConfig):
    prompt_driver: AmazonBedrockPromptDriver = field(
        default=Factory(
            lambda: AmazonBedrockPromptDriver(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                stream=False,
                prompt_model_driver=BedrockClaudePromptModelDriver(),
            )
        ),
        metadata={"serializable": True},
    )
    image_generation_driver: AmazonBedrockImageGenerationDriver = field(
        default=Factory(
            lambda: AmazonBedrockImageGenerationDriver(
                model="amazon.titan-image-generator-v1",
                image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
            )
        ),
        metadata={"serializable": True},
    )
    image_query_driver: AmazonBedrockImageQueryDriver = field(
        default=Factory(
            lambda: AmazonBedrockImageQueryDriver(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
            )
        ),
        metadata={"serializable": True},
    )
    embedding_driver: AmazonBedrockTitanEmbeddingDriver = field(
        default=Factory(lambda: AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-text-v1")),
        metadata={"serializable": True},
    )
    vector_store_driver: LocalVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(
                embedding_driver=AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-text-v1")
            )
        ),
        metadata={"serializable": True},
    )
