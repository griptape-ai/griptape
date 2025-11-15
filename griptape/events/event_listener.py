from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar, Union

from attrs import define, field

from .base_event import BaseEvent

if TYPE_CHECKING:
    from typing_extensions import Self

    from griptape.drivers.event_listener import BaseEventListenerDriver


T = TypeVar("T", bound=BaseEvent)


@define
class EventListener(Generic[T]):
    """An event listener that listens for events and handles them.

    Attributes:
        on_event: The on_event function that will be called when an event is published.
            The on_event function should accept an event and return either the event or a dictionary.
            Can be either a sync or async function. If the on_event returns None, the event will not be published.
        event_types: A list of event types that the event listener should listen for.
            If not provided, the event listener will listen for all event types.
        event_listener_driver: The driver that will be used to publish events.
    """

    on_event: Optional[
        Union[
            Callable[[T], Optional[BaseEvent | dict]],
            Callable[[T], asyncio.coroutines.Coroutine[None, None, Optional[BaseEvent | dict]]],
        ]
    ] = field(default=None)
    event_types: Optional[list[type[T]]] = field(default=None, kw_only=True)
    event_listener_driver: Optional[BaseEventListenerDriver] = field(default=None, kw_only=True)

    def __enter__(self) -> Self:
        from griptape.events import EventBus

        EventBus.add_event_listener(self)

        return self

    def __exit__(self, type, value, traceback) -> None:  # noqa: ANN001, A002
        from griptape.events import EventBus

        EventBus.remove_event_listener(self)

    def publish_event(self, event: T, *, flush: bool = False) -> None:
        """Publish an event synchronously."""
        event_types = self.event_types

        if event_types is None or any(isinstance(event, event_type) for event_type in event_types):
            handled_event = event
            if self.on_event is not None:
                # on_event must be sync for this method
                if inspect.iscoroutinefunction(self.on_event):
                    raise ValueError(
                        "on_event is an async function but publish_event was called synchronously. "
                        "Use apublish_event instead or provide a sync on_event handler."
                    )
                handled_event = self.on_event(event)

            if self.event_listener_driver is not None and handled_event is not None:
                self.event_listener_driver.publish_event(handled_event)

        if self.event_listener_driver is not None and flush:
            self.event_listener_driver.flush_events()

    async def apublish_event(self, event: T, *, flush: bool = False) -> None:
        """Publish an event asynchronously.

        This method supports both sync and async on_event handlers.
        """
        event_types = self.event_types

        if event_types is None or any(isinstance(event, event_type) for event_type in event_types):
            handled_event = event
            if self.on_event is not None:
                # Check if on_event is async
                if inspect.iscoroutinefunction(self.on_event):
                    handled_event = await self.on_event(event)
                else:
                    handled_event = self.on_event(event)

            if self.event_listener_driver is not None and handled_event is not None:
                self.event_listener_driver.publish_event(handled_event)

        if self.event_listener_driver is not None and flush:
            self.event_listener_driver.flush_events()
