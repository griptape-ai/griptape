from attrs import define, field
from griptape.events.base_event import BaseEvent

@define
class PromptEvent(BaseEvent):
    token_count = field(kw_only=True)
