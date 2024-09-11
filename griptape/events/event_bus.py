from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.mixins.singleton_mixin import SingletonMixin

if TYPE_CHECKING:
    from griptape.events import BaseEvent, EventListener


@define
class _EventBus(SingletonMixin):
    _event_listeners: list[EventListener] = field(factory=list, kw_only=True, alias="_event_listeners")
    _thread_lock: threading.Lock = field(default=Factory(lambda: threading.Lock()), alias="_thread_lock")

    @property
    def event_listeners(self) -> list[EventListener]:
        return self._event_listeners

    def add_event_listeners(self, event_listeners: list[EventListener]) -> list[EventListener]:
        return [self.add_event_listener(event_listener) for event_listener in event_listeners]

    def remove_event_listeners(self, event_listeners: list[EventListener]) -> None:
        for event_listener in event_listeners:
            self.remove_event_listener(event_listener)

    def add_event_listener(self, event_listener: EventListener) -> EventListener:
        with self._thread_lock:
            if event_listener not in self._event_listeners:
                self._event_listeners.append(event_listener)

        return event_listener

    def remove_event_listener(self, event_listener: EventListener) -> None:
        with self._thread_lock:
            if event_listener in self._event_listeners:
                self._event_listeners.remove(event_listener)

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        for event_listener in self._event_listeners:
            event_listener.publish_event(event, flush=flush)

    def clear_event_listeners(self) -> None:
        with self._thread_lock:
            self._event_listeners.clear()


EventBus = _EventBus()
