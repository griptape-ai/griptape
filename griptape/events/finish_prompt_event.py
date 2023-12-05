from attrs import define
from griptape.events.base_prompt_event import BasePromptEvent


@define
class FinishPromptEvent(BasePromptEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import FinishPromptEventSchema

        return dict(FinishPromptEventSchema().dump(self))
