from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.events import (
    BaseEvent,
    EventBus,
    EventListener,
    FinishStructureRunEvent,
)
from griptape.utils.contextvars_utils import with_contextvars

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.structures import Structure


@define
class Events:
    """A wrapper for Structures that converts `BaseChunkEvent`s into an iterator of TextArtifacts.

    It achieves this by running the Structure in a separate thread, listening for events from the Structure,
    and yielding those events.

    See relevant Stack Overflow post: https://stackoverflow.com/questions/9968592/turn-functions-with-a-callback-into-python-generators

    Attributes:
        structure: The Structure to wrap.
        _event_queue: A queue to hold events from the Structure.
    """

    structure: Structure = field()
    event_types: Optional[list[type[BaseEvent]]] = field(default=None, kw_only=True)

    _event_queue: Queue[BaseEvent] = field(default=Factory(lambda: Queue()))

    def run(self, *args) -> Iterator[BaseEvent]:
        t = Thread(target=with_contextvars(self._run_structure), args=args)
        t.start()

        while True:
            event = self._event_queue.get()
            yield event
            if isinstance(event, FinishStructureRunEvent):
                break
        t.join()

    def _run_structure(self, *args) -> None:
        def event_handler(event: BaseEvent) -> None:
            self._event_queue.put(event)

        event_types = [BaseEvent] if self.event_types is None else self.event_types
        if FinishStructureRunEvent not in event_types:
            event_types.append(FinishStructureRunEvent)
        stream_event_listener = EventListener(
            on_event=event_handler,
            event_types=event_types,
        )
        EventBus.add_event_listener(stream_event_listener)

        self.structure.run(*args)

        EventBus.remove_event_listener(stream_event_listener)
