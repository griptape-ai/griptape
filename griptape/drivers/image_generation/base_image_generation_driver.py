from abc import abstractmethod, ABC
from griptape.artifacts import ImageArtifact


class BaseImageGenerationDriver(ABC):
    @abstractmethod
    def generate_image(self, prompts: list[str], negative_prompts: list[str], **kwargs) -> ImageArtifact:
        ...
