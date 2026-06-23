from __future__ import annotations

from datetime import datetime

from attrs import define, field

from griptape.memory.meta import BaseMetaEntry


@define
class DateTimeMetaEntry(BaseMetaEntry):
    """Used to provide the current date and time as context to agents via MetaMemory.

    Attributes:
        todays_date_and_time: the current date and time formatted as YYYY-MM-DD HH:MM:SS.
    """

    type: str = field(default=BaseMetaEntry.__name__, kw_only=True, metadata={"serializable": False})
    todays_date_and_time: str = field(
        factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        kw_only=True,
        metadata={"serializable": True},
    )
