from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

from attrs import define, field

from .base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.drivers import BaseEventListenerDriver


T = TypeVar("T", bound=BaseEvent)


@define
class EventListener(Generic[T]):
    """An event listener that listens for events and handles them.

    Attributes:
        handler: The handler function that will be called when an event is published.
            The handler function should accept an event and return either the event or a dictionary.
            If the handler returns None, the event will not be published.
        event_types: A list of event types that the event listener should listen for.
            If not provided, the event listener will listen for all event types.
        event_listener_driver: The driver that will be used to publish events.
    """

    handler: Optional[Callable[[T], Optional[BaseEvent | dict]]] = field(default=None)
    event_types: Optional[list[type[T]]] = field(default=None, kw_only=True)
    event_listener_driver: Optional[BaseEventListenerDriver] = field(default=None, kw_only=True)

    _last_event_listeners: Optional[list[EventListener]] = field(default=None)

    def __enter__(self) -> EventListener:
        from griptape.events import EventBus

        EventBus.add_event_listener(self)

        return self

    def __exit__(self, type, value, traceback) -> None:  # noqa: ANN001, A002
        from griptape.events import EventBus

        EventBus.remove_event_listener(self)

        self._last_event_listeners = None

    def publish_event(self, event: T, *, flush: bool = False) -> None:
        event_types = self.event_types

        if event_types is None or type(event) in event_types:
            handled_event = event
            if self.handler is not None:
                handled_event = self.handler(event)

            if self.event_listener_driver is not None and handled_event is not None:
                self.event_listener_driver.publish_event(handled_event)

        if self.event_listener_driver is not None and flush:
            self.event_listener_driver.flush_events()
