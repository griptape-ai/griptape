from __future__ import annotations

import logging
from typing import Optional

from attrs import Factory, define, field
from rich.logging import RichHandler


@define
class LoggingConfig:
    logger_name: str = field(default="griptape", kw_only=True)
    level: int = field(default=logging.INFO, kw_only=True)
    handlers: list[logging.Handler] = field(
        default=Factory(lambda: [RichHandler(show_time=True, show_path=False)]), kw_only=True
    )
    propagate: bool = field(default=False, kw_only=True)
    handlers_formatter: Optional[logging.Formatter] = field(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.level)
        logger.propagate = self.propagate
        if self.handlers_formatter:
            for handler in self.handlers:
                handler.setFormatter(self.handlers_formatter)

        logger.handlers = self.handlers
