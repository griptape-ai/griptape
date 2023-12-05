from attrs import define
from griptape.events.base_prompt_event import BasePromptEvent


@define
class StartPromptEvent(BasePromptEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import StartPromptEventSchema

        return dict(StartPromptEventSchema().dump(self))
