from attrs import define

from griptape.configs.drivers import DriversConfig
from griptape.drivers import (
    GoogleEmbeddingDriver,
    GooglePromptDriver,
    LocalVectorStoreDriver,
)
from griptape.utils.decorators import lazy_property


@define
class GoogleDriversConfig(DriversConfig):
    @lazy_property()
    def prompt_driver(self) -> GooglePromptDriver:
        return GooglePromptDriver(model="gemini-1.5-pro")

    @lazy_property()
    def embedding_driver(self) -> GoogleEmbeddingDriver:
        return GoogleEmbeddingDriver(model="models/embedding-001")

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-001"))
