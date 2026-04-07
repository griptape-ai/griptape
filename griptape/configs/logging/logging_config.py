from __future__ import annotations

import logging

from attrs import define, field
from rich.logging import RichHandler


@define
class LoggingConfig:
    logger_name: str = field(default="griptape", kw_only=True)

    def __attrs_post_init__(self) -> None:
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.addHandler(RichHandler(show_time=True, show_path=False))
