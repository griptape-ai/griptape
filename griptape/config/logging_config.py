from __future__ import annotations

import logging

from attrs import define, field
from rich.logging import RichHandler


@define
class LoggingConfig:
    logger_name: str = field(default="griptape", kw_only=True)
    logger_level: int = field(
        default=logging.INFO,
        kw_only=True,
        on_setattr=lambda self, _, value: logging.getLogger(self.logger_name).setLevel(value),
    )

    def __attrs_post_init__(self) -> None:
        logger = logging.getLogger(self.logger_name)

        logger.propagate = False
        logger.setLevel(self.logger_level)

        logger.handlers = [RichHandler(show_time=True, show_path=False)]
