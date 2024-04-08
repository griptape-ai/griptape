from __future__ import annotations

from typing import Callable, Any
from attr import define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.events.base_event import BaseEvent


@define
class LocalEventListenerDriver(BaseEventListenerDriver):
    handler: Callable[[dict], Any] = field(default=None, kw_only=True)

    def publish_event(self, event: BaseEvent) -> None:
        self.try_publish_event(event)

    def try_publish_event(self, event: BaseEvent) -> None:
        self.handler({"event": event.to_dict()})
