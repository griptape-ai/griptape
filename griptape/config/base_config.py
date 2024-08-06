from abc import ABC

from attrs import define

from griptape.config.base_driver_config import BaseDriverConfig
from griptape.config.events_config import EventsConfig
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseConfig(SerializableMixin, ABC):
    drivers: BaseDriverConfig
    events: EventsConfig
