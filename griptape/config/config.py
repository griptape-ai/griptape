from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from .base_config import BaseConfig
from .drivers.openai_driver_config import OpenAiDriverConfig
from .logging.logging_config import LoggingConfig

if TYPE_CHECKING:
    from .drivers.base_driver_config import BaseDriverConfig


@define(kw_only=True)
class _Config(BaseConfig):
    logging_config: LoggingConfig = field(default=Factory(lambda: LoggingConfig()))
    driver_config: BaseDriverConfig = field(default=Factory(lambda: OpenAiDriverConfig()))


config = _Config()
