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
        default=Factory(lambda: GooglePromptDriver(model="gemini-1.5-pro")),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: GoogleEmbeddingDriver(model="models/embedding-001")),
        kw_only=True,
        metadata={"serializable": True},
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-001")),
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
