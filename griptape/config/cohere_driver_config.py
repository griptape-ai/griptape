from attrs import Factory, define, field

from griptape.config import DriverConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    CohereEmbeddingDriver,
    CoherePromptDriver,
    LocalVectorStoreDriver,
)


@define
class CohereDriverConfig(DriverConfig):
    api_key: str = field(metadata={"serializable": False}, kw_only=True)

    prompt: BasePromptDriver = field(
        default=Factory(lambda self: CoherePromptDriver(model="command-r", api_key=self.api_key), takes_self=True),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: CohereEmbeddingDriver(
                model="embed-english-v3.0",
                api_key=self.api_key,
                input_type="search_document",
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
