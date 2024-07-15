from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    CohereEmbeddingDriver,
    CoherePromptDriver,
    LocalVectorStoreDriver,
)


@define
class CohereStructureConfig(StructureConfig):
    api_key: str = field(metadata={"serializable": False}, kw_only=True)

    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda self: CoherePromptDriver(model="command-r", api_key=self.api_key), takes_self=True),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(
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
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding_driver), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
