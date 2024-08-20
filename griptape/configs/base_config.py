from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from .drivers.base_drivers_config import BaseDriversConfig
    from .logging.logging_config import LoggingConfig


@define(kw_only=True)
class BaseConfig(SerializableMixin, ABC):
    logging_config: LoggingConfig = field()
    drivers_config: BaseDriversConfig = field()
