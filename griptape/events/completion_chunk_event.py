from attr import field
from attrs import define
from griptape.events.base_event import BaseEvent


@define
class CompletionChunkEvent(BaseEvent):
    token: str = field(kw_only=True, metadata={"serializable": True})
