from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    AnthropicImageQueryDriver,
    AnthropicPromptDriver,
    BaseEmbeddingDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    LocalVectorStoreDriver,
    VoyageAiEmbeddingDriver,
)


@define
class AnthropicStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: AnthropicPromptDriver(model="claude-3-5-sonnet-20240620")),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: VoyageAiEmbeddingDriver(model="voyage-large-2")),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=VoyageAiEmbeddingDriver(model="voyage-large-2")),
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(lambda: AnthropicImageQueryDriver(model="claude-3-5-sonnet-20240620")),
        kw_only=True,
        metadata={"serializable": True},
    )
