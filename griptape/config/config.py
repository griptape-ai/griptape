from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from .base_config import BaseConfig
from .drivers.openai_driver_config import OpenAiDriverConfig
from .logging.logging_config import LoggingConfig

if TYPE_CHECKING:
    from .drivers.base_driver_config import BaseDriverConfig


@define(kw_only=True)
class _Config(BaseConfig):
    _logging: Optional[LoggingConfig] = field(default=None, alias="logging")
    _drivers: Optional[BaseDriverConfig] = field(default=None, alias="drivers")

    @property
    def drivers(self) -> BaseDriverConfig:
        """Lazily instantiates the drivers configuration to avoid client errors like missing API key."""
        if self._drivers is None:
            self._drivers = OpenAiDriverConfig()
        return self._drivers

    @drivers.setter
    def drivers(self, drivers: BaseDriverConfig) -> None:
        self._drivers = drivers

    @property
    def logging(self) -> LoggingConfig:
        if self._logging is None:
            self._logging = LoggingConfig()
        return self._logging

    @logging.setter
    def logging(self, logging: LoggingConfig) -> None:
        self._logging = logging


config = _Config()
