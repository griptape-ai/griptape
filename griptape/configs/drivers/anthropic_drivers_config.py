from attrs import define

from griptape.configs.drivers import DriversConfig
from griptape.drivers import (
    AnthropicImageQueryDriver,
    AnthropicPromptDriver,
    LocalVectorStoreDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.utils.decorators import lazy_property


@define
class AnthropicDriversConfig(DriversConfig):
    @lazy_property()
    def prompt_driver(self) -> AnthropicPromptDriver:
        return AnthropicPromptDriver(model="claude-3-5-sonnet-20240620")

    @lazy_property()
    def embedding_driver(self) -> VoyageAiEmbeddingDriver:
        return VoyageAiEmbeddingDriver(model="voyage-large-2")

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=VoyageAiEmbeddingDriver(model="voyage-large-2"))

    @lazy_property()
    def image_query_driver(self) -> AnthropicImageQueryDriver:
        return AnthropicImageQueryDriver(model="claude-3-5-sonnet-20240620")
