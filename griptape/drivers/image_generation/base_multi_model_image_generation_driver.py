from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional, TYPE_CHECKING

from attr import field, define

from griptape.artifacts import ImageArtifact
from .base_image_generation_driver import BaseImageGenerationDriver

if TYPE_CHECKING:
    from griptape.drivers import BaseImageGenerationModelDriver


@define
class BaseMultiModelImageGenerationDriver(BaseImageGenerationDriver, ABC):
    """Image Generation Driver for platforms like Amazon Bedrock that host many LLM models.

    Instances of this Image Generation Driver require a Image Generation Model Driver which is used to structure the
    image generation request in the format required by the model and to process the output.

    Attributes:
        model: Name of the model to use.
        image_generation_model_driver: Image Generation Model Driver to use.
    """

    image_generation_model_driver: BaseImageGenerationModelDriver = field(kw_only=True)

    @abstractmethod
    def try_generate_image(self, prompts: list[str], negative_prompts: list[str] | None = None) -> ImageArtifact:
        ...
