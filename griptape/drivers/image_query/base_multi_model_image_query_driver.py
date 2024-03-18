from __future__ import annotations
from abc import ABC

from attr import field, define

from griptape.drivers import BaseImageQueryDriver, BaseImageQueryModelDriver


@define
class BaseMultiModelImageQueryDriver(BaseImageQueryDriver, ABC):
    """Image Query Driver for platforms like Amazon Bedrock that host many LLM models.

    Instances of this Image QUery Driver require a Image Query Model Driver which is used to structure the
    image generation request in the format required by the model and to process the output.

    Attributes:
        image_query_model_driver: Image Model Driver to use.
    """
    model: str = field(default="claude-3-sonnet-20240229", kw_only=True, metadata={"serializable": True})
    image_query_model_driver: BaseImageQueryModelDriver = field(kw_only=True, metadata={"serializable": True})
