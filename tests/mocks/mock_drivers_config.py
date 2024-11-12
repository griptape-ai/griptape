from attrs import define

from griptape.configs.drivers import DriversConfig
from griptape.drivers.vector.local_vector_store_driver import LocalVectorStoreDriver
from griptape.utils.decorators import lazy_property
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


@define
class MockDriversConfig(DriversConfig):
    @lazy_property()
    def prompt_driver(self) -> MockPromptDriver:
        return MockPromptDriver()

    @lazy_property()
    def image_generation_driver(self) -> MockImageGenerationDriver:
        return MockImageGenerationDriver()

    @lazy_property()
    def embedding_driver(self) -> MockEmbeddingDriver:
        return MockEmbeddingDriver()

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
