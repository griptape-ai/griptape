from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.drivers.image_generation import BaseImageGenerationDriver

if TYPE_CHECKING:
    from griptape.drivers.image_generation_model import BaseImageGenerationModelDriver


@define
class BaseMultiModelImageGenerationDriver(BaseImageGenerationDriver, ABC):
    """Image Generation Driver for platforms like Amazon Bedrock that host many LLM models.

    Instances of this Image Generation Driver require a Image Generation Model Driver which is used to structure the
    image generation request in the format required by the model and to process the output.

    Attributes:
        image_generation_model_driver: Image Model Driver to use.
    """

    image_generation_model_driver: BaseImageGenerationModelDriver = field(kw_only=True, metadata={"serializable": True})
