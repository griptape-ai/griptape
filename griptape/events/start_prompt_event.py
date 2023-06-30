from attrs import define, field
from griptape.events.base_event import BaseEvent


@define
class StartPromptEvent(BaseEvent):
    token_count: int = field(kw_only=True)
