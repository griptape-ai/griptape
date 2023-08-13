import time
from abc import ABC
from attr import define, field, Factory


@define
class BaseEvent(ABC):
    timestamp: float = field(
        default=Factory(lambda: time.time()), kw_only=True
    )
