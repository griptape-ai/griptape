from attrs import define, field

from griptape.events.base_event import BaseEvent


@define
class CompletionChunkEvent(BaseEvent):
    token: str = field(kw_only=True, metadata={"serializable": True})
