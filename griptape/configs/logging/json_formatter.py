import json
import logging
from typing import Any

from attrs import define, field


@define
class JsonFormatter(logging.Formatter):
    indent: int = field(default=2, kw_only=True)

    def __attrs_pre_init__(self) -> None:
        super().__init__()

    def format(self, record: Any) -> str:
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, indent=self.indent)

        return super().format(record)
