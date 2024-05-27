from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    AmazonBedrockImageGenerationDriver,
    AmazonBedrockImageQueryDriver,
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    BedrockClaudeImageQueryModelDriver,
    BedrockClaudePromptModelDriver,
    BedrockTitanImageGenerationModelDriver,
    LocalVectorStoreDriver,
)


@define()
class AmazonBedrockStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: self._factory(
                AmazonBedrockPromptDriver,
                "prompt_driver",
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                prompt_model_driver=BedrockClaudePromptModelDriver(),
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: self._factory(
                AmazonBedrockImageGenerationDriver,
                "image_generation_driver",
                model="amazon.titan-image-generator-v1",
                image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: self._factory(
                AmazonBedrockImageQueryDriver,
                "image_query_driver",
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: self._factory(
                AmazonBedrockTitanEmbeddingDriver, "embedding_driver", model="amazon.titan-embed-text-v1"
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda self: self._factory(
                LocalVectorStoreDriver, "vector_store_driver", embedding_driver=self.embedding_driver
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
