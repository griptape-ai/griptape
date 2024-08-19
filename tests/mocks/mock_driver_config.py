from attrs import define

from griptape.config.drivers import DriverConfig
from griptape.drivers.vector.local_vector_store_driver import LocalVectorStoreDriver
from griptape.utils.decorators import lazy_property
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


@define
class MockDriverConfig(DriverConfig):
    @lazy_property()
    def prompt(self) -> MockPromptDriver:
        return MockPromptDriver()

    @lazy_property()
    def image_generation(self) -> MockImageGenerationDriver:
        return MockImageGenerationDriver()

    @lazy_property()
    def image_query(self) -> MockImageQueryDriver:
        return MockImageQueryDriver()

    @lazy_property()
    def embedding(self) -> MockEmbeddingDriver:
        return MockEmbeddingDriver()

    @lazy_property()
    def vector_store(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
