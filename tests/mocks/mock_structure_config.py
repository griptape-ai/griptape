from attrs import Factory, define, field

from griptape.config import StructureConfig
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


@define
class MockStructureConfig(StructureConfig):
    prompt_driver: MockPromptDriver = field(
        default=Factory(lambda: MockPromptDriver()), metadata={"serializable": True}
    )
    image_generation_driver: MockImageGenerationDriver = field(
        default=Factory(lambda: MockImageGenerationDriver(model="dall-e-2")), metadata={"serializable": True}
    )
    embedding_driver: MockEmbeddingDriver = field(
        default=Factory(lambda: MockEmbeddingDriver(model="text-embedding-3-small")), metadata={"serializable": True}
    )
