from attrs import define
from griptape.utils import PromptStack
from attrs import field
from griptape.events.base_prompt_event import BasePromptEvent


@define
class StartPromptEvent(BasePromptEvent):
    prompt_stack: PromptStack = field(kw_only=True)
    prompt: str = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import StartPromptEventSchema

        return dict(StartPromptEventSchema().dump(self))
