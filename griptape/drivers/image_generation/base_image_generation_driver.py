from abc import abstractmethod, ABC
from typing import Optional

from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.mixins import ExponentialBackoffMixin


@define
class BaseImageGenerationDriver(ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True)

    def generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                return self.try_generate_image(prompts=prompts, negative_prompts=negative_prompts)

    @abstractmethod
    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...
