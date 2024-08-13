from attrs import Factory, define, field

from griptape.config import DriverConfig
from griptape.drivers.vector.local_vector_store_driver import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


@define
class MockDriverConfig(DriverConfig):
    prompt: MockPromptDriver = field(default=Factory(lambda: MockPromptDriver()), metadata={"serializable": True})
    image_generation: MockImageGenerationDriver = field(
        default=Factory(lambda: MockImageGenerationDriver()),
        metadata={"serializable": True},
    )
    image_query: MockImageQueryDriver = field(
        default=Factory(lambda: MockImageQueryDriver()), metadata={"serializable": True}
    )
    embedding: MockEmbeddingDriver = field(
        default=Factory(lambda: MockEmbeddingDriver()), metadata={"serializable": True}
    )
    vector_store: LocalVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding), takes_self=True),
        metadata={"serializable": True},
    )
