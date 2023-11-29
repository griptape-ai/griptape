from abc import ABC

from attr import define, field

from griptape.mixins import ExponentialBackoffMixin


@define
class BaseImageGenerationDriver(ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True)
