from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field

if TYPE_CHECKING:
    from griptape.drivers import BaseEventListenerDriver

    from .base_event import BaseEvent

_active_listeners: contextvars.ContextVar[list[EventListener]] = contextvars.ContextVar(
    "active_event_listeners", default=[]
)


@define
class EventListener:
    handler: Callable[[BaseEvent], Optional[dict]] = field(default=Factory(lambda: lambda event: event.to_dict()))
    event_types: Optional[list[type[BaseEvent]]] = field(default=None, kw_only=True)
    driver: Optional[BaseEventListenerDriver] = field(default=None, kw_only=True)

    _last_event_listeners: Optional[list[EventListener]] = field(default=None)

    def __enter__(self) -> EventListener:
        # Add this listener to the active listeners stack
        listeners = _active_listeners.get()
        _active_listeners.set(listeners + [self])
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Remove this listener from the active listeners stack
        listeners = _active_listeners.get()
        if self in listeners:
            listeners.remove(self)
            _active_listeners.set(listeners)

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        event_types = self.event_types

        if event_types is None or type(event) in event_types:
            event_payload = self.handler(event)
            if self.driver is not None:
                if event_payload is not None and isinstance(event_payload, dict):
                    self.driver.publish_event(event_payload, flush=flush)
                else:
                    self.driver.publish_event(event, flush=flush)
