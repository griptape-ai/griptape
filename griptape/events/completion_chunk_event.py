from attr import field
from attrs import define
from griptape.events.base_event import BaseEvent


@define
class CompletionChunkEvent(BaseEvent):
    token: str = field(kw_only=True)

    def to_dict(self):
        from griptape.schemas import CompletionChunkEventSchema

        return dict(CompletionChunkEventSchema().dump(self))
