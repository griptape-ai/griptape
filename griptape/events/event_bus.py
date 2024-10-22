from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.events import BaseEvent
from griptape.mixins.singleton_mixin import SingletonMixin

if TYPE_CHECKING:
    from griptape.events import EventListener


@define
class _EventBus(SingletonMixin):
    _thread_data: threading.local = field(factory=threading.local, kw_only=True, alias="_thread_data")
    _global_listeners: list[EventListener] = field(factory=list, alias="_global_listeners")
    _thread_lock: threading.Lock = field(default=Factory(lambda: threading.Lock()), alias="_thread_lock")

    @property
    def event_listeners(self) -> list[EventListener]:
        return self.global_listeners + self.local_listeners

    @property
    def local_listeners(self) -> list[EventListener]:
        if not hasattr(self._thread_data, "event_listeners"):
            self._thread_data.event_listeners = []
        return self._thread_data.event_listeners

    @property
    def global_listeners(self) -> list[EventListener]:
        return self._global_listeners

    def add_event_listener(self, event_listener: EventListener) -> EventListener:
        with self._thread_lock:
            if event_listener.is_thread_local:
                if event_listener not in self.local_listeners:
                    self.local_listeners.append(event_listener)
            else:
                if event_listener not in self.global_listeners:
                    self.global_listeners.append(event_listener)

        return event_listener

    def remove_event_listener(self, event_listener: EventListener) -> None:
        with self._thread_lock:
            if event_listener.is_thread_local:
                if event_listener in self.local_listeners:
                    self.local_listeners.remove(event_listener)
            else:
                if event_listener in self.global_listeners:
                    self.global_listeners.remove(event_listener)

    def add_event_listeners(self, event_listeners: list[EventListener]) -> list[EventListener]:
        return [self.add_event_listener(event_listener) for event_listener in event_listeners]

    def remove_event_listeners(self, event_listeners: list[EventListener]) -> None:
        for event_listener in event_listeners:
            self.remove_event_listener(event_listener)

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        for event_listener in self.event_listeners:
            event_listener.publish_event(event, flush=flush)

    def clear_event_listeners(self) -> None:
        with self._thread_lock:
            self.event_listeners.clear()


EventBus = _EventBus()
