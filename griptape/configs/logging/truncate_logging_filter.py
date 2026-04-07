import logging
from typing import Any

from attrs import define, field


@define
class TruncateLoggingFilter(logging.Filter):
    max_log_length: int = field(default=1000, kw_only=True)

    def filter(self, record: Any) -> bool:
        message = record.getMessage()

        if len(message) > self.max_log_length:
            record.msg = f"{message[: self.max_log_length]}... [{len(message) - self.max_log_length} more characters]"
            record.args = ()
        return True
