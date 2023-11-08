from typing import Callable, Optional, Type, Any
from attrs import define, field
from .base_event import BaseEvent


@define
class EventListener:
    handler: Callable[[BaseEvent], Any] = field()
    event_types: Optional[list[Type[BaseEvent]]] = field(default=None, kw_only=True)
