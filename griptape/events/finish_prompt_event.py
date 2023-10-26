from attr import field
from attrs import define
from griptape.events.base_event import BaseEvent


@define
class FinishPromptEvent(BaseEvent):
    token_count: int = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import FinishPromptEventSchema

        return dict(FinishPromptEventSchema().dump(self))
