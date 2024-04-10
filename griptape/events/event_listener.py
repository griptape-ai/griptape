from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from attrs import define, field
from .base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.drivers import BaseEventListenerDriver


@define
class EventListener:
    event_types: Optional[list[type[BaseEvent]]] = field(default=None, kw_only=True)
    driver: Optional[BaseEventListenerDriver] = field(default=None, kw_only=True)

    def publish_event(self, event: BaseEvent) -> None:
        event_types = self.event_types

        if event_types is None or type(event) in event_types:
            if self.driver is not None:
                self.driver.publish_event(event)
