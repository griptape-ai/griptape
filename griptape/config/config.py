from attrs import define

from griptape.config.base_config import BaseConfig
from griptape.config.base_structure_config import BaseStructureConfig
from griptape.mixins.event_publisher_mixin import EventPublisherMixin

from .openai_structure_config import OpenAiStructureConfig


@define
class _Config(BaseConfig, EventPublisherMixin):
    drivers: BaseStructureConfig


Config = _Config(
    drivers=OpenAiStructureConfig(),
)
