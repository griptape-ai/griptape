from attrs import define, field
from griptape.events.base_event import BaseEvent

@define
class StartPromptEvent(BaseEvent):
    token_count: str = field(kw_only=True)
