from attrs import define

from griptape.configs.drivers import DriversConfig
from griptape.drivers.embedding.google import GoogleEmbeddingDriver
from griptape.drivers.prompt.google import GooglePromptDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.utils.decorators import lazy_property


@define
class GoogleDriversConfig(DriversConfig):
    @lazy_property()
    def prompt_driver(self) -> GooglePromptDriver:
        return GooglePromptDriver(model="gemini-2.0-flash")

    @lazy_property()
    def embedding_driver(self) -> GoogleEmbeddingDriver:
        return GoogleEmbeddingDriver(model="models/embedding-004")

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-004"))
