from attrs import define
from griptape.events.base_event import BaseEvent


@define
class StartStructureRunEvent(BaseEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import StartStructureRunEventSchema

        return dict(StartStructureRunEventSchema().dump(self))
