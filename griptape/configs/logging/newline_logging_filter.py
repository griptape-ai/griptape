import logging
from typing import Any

from attrs import define, field


@define
class NewlineLoggingFilter(logging.Filter):
    replace_str: str = field(default=" ", kw_only=True)

    def filter(self, record: Any) -> bool:
        record.msg = record.msg.replace("\n", self.replace_str)
        return True
