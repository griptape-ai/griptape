from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

from attrs import define

from griptape.mixins.singleton_mixin import SingletonMixin

if TYPE_CHECKING:
    from griptape.events import BaseEvent, EventListener


# Context Vars must be declared at the top module level.
# Also, in-place modifications do not trigger the context var's `set` method
# so we must reassign the context var with the new value when adding or removing event listeners.
_event_listeners: ContextVar[Optional[list[EventListener]]] = ContextVar("event_listeners", default=None)


@define
class _EventBus(SingletonMixin):
    @property
    def event_listeners(self) -> list[EventListener]:
        event_listeners_val = _event_listeners.get()
        if event_listeners_val is None:
            event_listeners_val = []
            _event_listeners.set(event_listeners_val)
        return event_listeners_val

    @event_listeners.setter
    def event_listeners(self, event_listeners: list[EventListener]) -> None:
        _event_listeners.set(event_listeners)

    def add_event_listeners(self, event_listeners: list[EventListener]) -> list[EventListener]:
        return [self.add_event_listener(event_listener) for event_listener in event_listeners]

    def remove_event_listeners(self, event_listeners: list[EventListener]) -> None:
        for event_listener in event_listeners:
            self.remove_event_listener(event_listener)

    def add_event_listener(self, event_listener: EventListener) -> EventListener:
        if event_listener not in self.event_listeners:
            self.event_listeners = self.event_listeners + [event_listener]

        return event_listener

    def remove_event_listener(self, event_listener: EventListener) -> None:
        if event_listener in self.event_listeners:
            self.event_listeners = [listener for listener in self.event_listeners if listener != event_listener]

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        for event_listener in self.event_listeners:
            event_listener.publish_event(event, flush=flush)

    def clear_event_listeners(self) -> None:
        self.event_listeners = []


EventBus = _EventBus()
