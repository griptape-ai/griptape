from abc import abstractmethod, ABC
from typing import Optional

from attr import define, field

from griptape.artifacts import ImageArtifact


@define
class BaseImageGenerationDriver(ABC):
    model: str = field(kw_only=True)

    @abstractmethod
    def generate_image(
        self, prompts: list[str], negative_prompts: Optional[list[str]] = None, **kwargs
    ) -> ImageArtifact:
        ...
