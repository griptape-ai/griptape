from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from griptape.events import BaseEvent, EventListener


@define
class EventPublisherMixin:
    event_listeners: list[EventListener] = field(factory=list, kw_only=True)

    def add_event_listeners(self, event_listeners: list[EventListener]) -> list[EventListener]:
        return [self.add_event_listener(event_listener) for event_listener in event_listeners]

    def remove_event_listeners(self, event_listeners: list[EventListener]) -> None:
        for event_listener in event_listeners:
            self.remove_event_listener(event_listener)

    def add_event_listener(self, event_listener: EventListener) -> EventListener:
        if event_listener not in self.event_listeners:
            self.event_listeners.append(event_listener)

        return event_listener

    def remove_event_listener(self, event_listener: EventListener) -> None:
        if event_listener in self.event_listeners:
            self.event_listeners.remove(event_listener)

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        for event_listener in self.event_listeners:
            event_listener.publish_event(event, flush=flush)
