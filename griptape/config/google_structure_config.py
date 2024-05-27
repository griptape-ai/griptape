from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    GoogleEmbeddingDriver,
    GooglePromptDriver,
    LocalVectorStoreDriver,
)


@define
class GoogleStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: self._factory(GooglePromptDriver, "prompt_driver", model="gemini-pro"), takes_self=True
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: self._factory(GoogleEmbeddingDriver, "embedding_driver", model="models/embedding-001"),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
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
