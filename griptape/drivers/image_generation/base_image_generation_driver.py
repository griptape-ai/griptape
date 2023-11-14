from abc import abstractmethod, ABC

from attr import define, field

from griptape.artifacts import ImageArtifact


@define
class BaseImageGenerationDriver(ABC):
    model: str = field(kw_only=True)

    @abstractmethod
    def generate_image(self, prompts: list[str], negative_prompts: list[str] = list, **kwargs) -> ImageArtifact:
        ...
