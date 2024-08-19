from attrs import define

from griptape.config.drivers import DriverConfig
from griptape.drivers import (
    AnthropicImageQueryDriver,
    AnthropicPromptDriver,
    LocalVectorStoreDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.utils.decorators import lazy_property


@define
class AnthropicDriverConfig(DriverConfig):
    @lazy_property()
    def prompt(self) -> AnthropicPromptDriver:
        return AnthropicPromptDriver(model="claude-3-5-sonnet-20240620")

    @lazy_property()
    def embedding(self) -> VoyageAiEmbeddingDriver:
        return VoyageAiEmbeddingDriver(model="voyage-large-2")

    @lazy_property()
    def vector_store(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=VoyageAiEmbeddingDriver(model="voyage-large-2"))

    @lazy_property()
    def image_query(self) -> AnthropicImageQueryDriver:
        return AnthropicImageQueryDriver(model="claude-3-5-sonnet-20240620")
