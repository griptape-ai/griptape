from attrs import Factory, define, field

from .base_config import BaseConfig
from .base_driver_config import BaseDriverConfig
from .events_config import EventsConfig
from .openai_driver_config import OpenAiDriverConfig


@define
class _Config(BaseConfig):
    drivers: BaseDriverConfig = field(default=Factory(lambda: OpenAiDriverConfig()), kw_only=True)
    events: EventsConfig = field(default=Factory(lambda: EventsConfig()), kw_only=True)


Config = _Config()
