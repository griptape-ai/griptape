from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field

if TYPE_CHECKING:
    from griptape.drivers import BaseEventListenerDriver

    from .base_event import BaseEvent


@define
class EventListener:
    handler: Callable[[BaseEvent], Optional[dict]] = field(default=Factory(lambda: lambda event: event.to_dict()))
    event_types: Optional[list[type[BaseEvent]]] = field(default=None, kw_only=True)
    driver: Optional[BaseEventListenerDriver] = field(default=None, kw_only=True)

    _last_event_listeners: Optional[list[EventListener]] = field(default=None)

    def __enter__(self) -> EventListener:
        from griptape.events import EventBus

        EventBus.add_event_listener(self)

        return self

    def __exit__(self, type, value, traceback) -> None:  # noqa: ANN001, A002
        from griptape.events import EventBus

        EventBus.remove_event_listener(self)

        self._last_event_listeners = None

    def publish_event(self, event: BaseEvent, *, flush: bool = False) -> None:
        event_types = self.event_types

        if event_types is None or type(event) in event_types:
            event_payload = self.handler(event)
            if self.driver is not None:
                if event_payload is not None and isinstance(event_payload, dict):
                    self.driver.publish_event(event_payload, flush=flush)
                else:
                    self.driver.publish_event(event, flush=flush)
