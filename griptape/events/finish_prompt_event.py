from attrs import define, field
from griptape.events.base_prompt_event import BasePromptEvent


@define
class FinishPromptEvent(BasePromptEvent):
    result: str = field(kw_only=True, metadata={"serializable": True})
