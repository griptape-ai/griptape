from attrs import define
from griptape.events.base_event import BaseEvent


@define
class FinishStructureRunEvent(BaseEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import FinishStructureRunEventSchema

        return dict(FinishStructureRunEventSchema().dump(self))
