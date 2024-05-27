from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiImageQueryDriver,
)


@define
class OpenAiStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: self._factory(OpenAiChatPromptDriver, "prompt_driver", model="gpt-4o"), takes_self=True
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: self._factory(
                OpenAiImageGenerationDriver, "image_generation_driver", model="dall-e-2", image_size="512x512"
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(
            lambda self: self._factory(OpenAiImageQueryDriver, "image_query_driver", model="gpt-4o"), takes_self=True
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: self._factory(OpenAiEmbeddingDriver, "embedding_driver", model="text-embedding-3-small"),
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
