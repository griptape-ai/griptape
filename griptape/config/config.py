from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.utils.decorators import lazy_property

from .base_config import BaseConfig
from .drivers.openai_driver_config import OpenAiDriverConfig
from .logging.logging_config import LoggingConfig

if TYPE_CHECKING:
    from .drivers.base_driver_config import BaseDriverConfig


@define(kw_only=True)
class _Config(BaseConfig):
    _logging_config: Optional[LoggingConfig] = field(default=None, alias="logging")
    _driver_config: Optional[BaseDriverConfig] = field(default=None, alias="drivers")

    @lazy_property()
    def driver_config(self) -> BaseDriverConfig:
        return OpenAiDriverConfig()

    @lazy_property()
    def logging_config(self) -> LoggingConfig:
        return LoggingConfig()


config = _Config()
