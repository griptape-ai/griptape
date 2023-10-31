from attrs import define, field
from griptape.events.base_event import BaseEvent


@define
class StartPromptEvent(BaseEvent):
    token_count: int = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import StartPromptEventSchema

        return dict(StartPromptEventSchema().dump(self))
