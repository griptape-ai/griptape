from attrs import define, field

from griptape.events.base_event import BaseEvent


@define
class BaseChunkEvent(BaseEvent):
    index: int = field(default=0, metadata={"serializable": True})

    def __str__(self) -> str: ...
