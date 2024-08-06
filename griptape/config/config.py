from attrs import define

from griptape.config.base_config import BaseConfig
from griptape.config.base_driver_config import BaseDriverConfig
from griptape.mixins.event_publisher_mixin import EventPublisherMixin

from .openai_driver_config import OpenAiDriverConfig


@define
class _Config(BaseConfig, EventPublisherMixin):
    drivers: BaseDriverConfig


Config = _Config(
    drivers=OpenAiDriverConfig(),
)
