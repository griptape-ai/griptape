from __future__ import annotations

from attr import field, define

from griptape.drivers import BaseImageDriver, BaseImageModelDriver


@define
class BaseMultiModelImageDriver(BaseImageDriver):
    """Image Modification Driver for platforms like Amazon Bedrock that host many LLM models.

    Instances of this Image Generation Driver require a Image Generation Model Driver which is used to structure the
    image generation request in the format required by the model and to process the output.

    Attributes:
        image_model_driver: Image Model Driver to use.
    """

    image_model_driver: BaseImageModelDriver = field(kw_only=True)
