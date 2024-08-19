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
    _logging_config: Optional[LoggingConfig] = field(default=None, alias="logging")
    _driver_config: Optional[BaseDriverConfig] = field(default=None, alias="drivers")

    @property
    def driver_config(self) -> BaseDriverConfig:
        """Lazily instantiates the drivers configuration to avoid client errors like missing API key."""
        if self._driver_config is None:
            self._driver_config = OpenAiDriverConfig()
        return self._driver_config

    @driver_config.setter
    def driver_config(self, drivers: BaseDriverConfig) -> None:
        self._driver_config = drivers

    @property
    def logging_config(self) -> LoggingConfig:
        if self._logging_config is None:
            self._logging_config = LoggingConfig()
        return self._logging_config

    @logging_config.setter
    def logging_config(self, logging: LoggingConfig) -> None:
        self._logging_config = logging


config = _Config()
