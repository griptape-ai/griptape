from attrs import Factory, define, field

from .base_config import BaseConfig
from .base_driver_config import BaseDriverConfig
from .logging_config import LoggingConfig
from .openai_driver_config import OpenAiDriverConfig


@define(kw_only=True)
class _Config(BaseConfig):
    logging: LoggingConfig = field(default=Factory(lambda: LoggingConfig()))
    _drivers: BaseDriverConfig = field(default=None)

    @property
    def drivers(self) -> BaseDriverConfig:
        """Lazily instantiates the drivers configuration to avoid client errors like missing API key."""
        if self._drivers is None:
            self._drivers = OpenAiDriverConfig()
        return self._drivers

    @drivers.setter
    def drivers(self, drivers: BaseDriverConfig) -> None:
        self._drivers = drivers


config = _Config()
