from attrs import define

from griptape.config.drivers import DriverConfig
from griptape.drivers import (
    GoogleEmbeddingDriver,
    GooglePromptDriver,
    LocalVectorStoreDriver,
)
from griptape.utils.decorators import lazy_property


@define
class GoogleDriverConfig(DriverConfig):
    @lazy_property()
    def prompt(self) -> GooglePromptDriver:
        return GooglePromptDriver(model="gemini-1.5-pro")

    @lazy_property()
    def embedding(self) -> GoogleEmbeddingDriver:
        return GoogleEmbeddingDriver(model="models/embedding-001")

    @lazy_property()
    def vector_store(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-001"))
