from attr import field
from attrs import define
from griptape.events.base_event import BaseEvent


@define
class FinishPromptEvent(BaseEvent):
    token_count: int = field(kw_only=True)
