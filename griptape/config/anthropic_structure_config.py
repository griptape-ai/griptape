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
        default=Factory(
            lambda self: self._factory(AnthropicPromptDriver, "prompt_driver", model="claude-3-opus-20240229"),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: self._factory(VoyageAiEmbeddingDriver, "embedding_driver", model="voyage-large-2"),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda self: self._factory(
                LocalVectorStoreDriver, "vector_store_driver", embedding_driver=self.embedding_driver
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(
            lambda self: self._factory(AnthropicImageQueryDriver, "image_query_driver", model="claude-3-opus-20240229"),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
