from abc import ABC

from attrs import define

from griptape.mixins.serializable_mixin import SerializableMixin

from .base_driver_config import BaseDriverConfig
from .logging_config import LoggingConfig


@define(kw_only=True)
class BaseConfig(SerializableMixin, ABC):
    drivers: BaseDriverConfig
    logging: LoggingConfig
