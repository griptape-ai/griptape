from attrs import define, field
from griptape.events.base_prompt_event import BasePromptEvent


@define
class FinishPromptEvent(BasePromptEvent):
    result: str = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import FinishPromptEventSchema

        return dict(FinishPromptEventSchema().dump(self))
