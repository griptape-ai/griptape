from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageToImageGenerationDriver
from griptape.drivers.image_model.base_combined_generation_model_driver import BaseCombinedGenerationModelDriver


@define
class BaseMultiModelCombinedGenerationDriver(BaseImageToImageGenerationDriver):
    # TODO docstring
    """Image Modification Driver for platforms like Amazon Bedrock that host many LLM models.

    Instances of this Image Generation Driver require a Image Generation Model Driver which is used to structure the
    image generation request in the format required by the model and to process the output.

    Attributes:
        model: Name of the model to use.
        image_generation_model_driver: Image Model Driver to use.
    """

    image_generation_model_driver: BaseCombinedGenerationModelDriver = field(kw_only=True)

    @abstractmethod
    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...
