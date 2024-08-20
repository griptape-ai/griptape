from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from .base_config import BaseConfig
from .drivers.openai_drivers_config import OpenAiDriversConfig
from .logging.logging_config import LoggingConfig

if TYPE_CHECKING:
    from .drivers.base_drivers_config import BaseDriversConfig


@define(kw_only=True)
class _DefaultsConfig(BaseConfig):
    _instance = None

    def __new__(cls, *args, **kwargs) -> _DefaultsConfig:
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)  # noqa: UP008
        return cls._instance

    logging_config: LoggingConfig = field(default=Factory(lambda: LoggingConfig()))
    drivers_config: BaseDriversConfig = field(default=Factory(lambda: OpenAiDriversConfig()))


Defaults = _DefaultsConfig()
