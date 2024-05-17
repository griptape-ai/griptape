from attrs import define, field, Factory

from griptape.config import StructureConfig
from griptape.drivers import (
    AnthropicImageQueryDriver,
    AnthropicPromptDriver,
    LocalVectorStoreDriver,
    VoyageAiEmbeddingDriver,
)


@define
class AnthropicStructureConfig(StructureConfig):
    prompt_driver: AnthropicPromptDriver = field(
        default=Factory(lambda: AnthropicPromptDriver(model="claude-3-opus-20240229")),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding_driver: VoyageAiEmbeddingDriver = field(
        default=Factory(lambda: VoyageAiEmbeddingDriver(model="voyage-large-2")),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: LocalVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=VoyageAiEmbeddingDriver(model="voyage-large-2"))
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: AnthropicImageQueryDriver = field(
        default=Factory(lambda: AnthropicImageQueryDriver(model="claude-3-opus-20240229")),
        kw_only=True,
        metadata={"serializable": True},
    )
