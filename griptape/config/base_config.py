from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from .drivers.base_driver_config import BaseDriverConfig
    from .logging.logging_config import LoggingConfig


@define(kw_only=True)
class BaseConfig(SerializableMixin, ABC):
    _logging_config: Optional[LoggingConfig] = field(alias="logging")
    _driver_config: Optional[BaseDriverConfig] = field(alias="drivers")

    def reset(self) -> None:
        self._logging_config = None
        self._driver_config = None
