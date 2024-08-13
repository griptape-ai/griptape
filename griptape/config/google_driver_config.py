from attrs import Factory, define, field

from griptape.config import DriverConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    GoogleEmbeddingDriver,
    GooglePromptDriver,
    LocalVectorStoreDriver,
)


@define
class GoogleDriverConfig(DriverConfig):
    prompt: BasePromptDriver = field(
        default=Factory(lambda: GooglePromptDriver(model="gemini-1.5-pro")),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding: BaseEmbeddingDriver = field(
        default=Factory(lambda: GoogleEmbeddingDriver(model="models/embedding-001")),
        kw_only=True,
        metadata={"serializable": True},
    )
    vector_store: BaseVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-001")),
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
