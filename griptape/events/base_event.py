from datetime import datetime
from abc import ABC
from attr import define, field, Factory


@define
class BaseEvent(ABC):
    timestamp: datetime = field(
        default=Factory(lambda: datetime.now()), kw_only=True
    )
