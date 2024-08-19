from attrs import define, field

from griptape.config.drivers import DriverConfig
from griptape.drivers import (
    CohereEmbeddingDriver,
    CoherePromptDriver,
    LocalVectorStoreDriver,
)
from griptape.utils.decorators import lazy_property


@define
class CohereDriverConfig(DriverConfig):
    api_key: str = field(metadata={"serializable": False}, kw_only=True)

    @lazy_property()
    def prompt(self) -> CoherePromptDriver:
        return CoherePromptDriver(model="command-r", api_key=self.api_key)

    @lazy_property()
    def embedding(self) -> CohereEmbeddingDriver:
        return CohereEmbeddingDriver(
            model="embed-english-v3.0",
            api_key=self.api_key,
            input_type="search_document",
        )

    @lazy_property()
    def vector_store(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(
            embedding_driver=CohereEmbeddingDriver(
                model="embed-english-v3.0",
                api_key=self.api_key,
                input_type="search_document",
            )
        )
