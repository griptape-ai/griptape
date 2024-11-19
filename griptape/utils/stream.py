from __future__ import annotations

import json
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.events import (
    ActionChunkEvent,
    BaseChunkEvent,
    EventBus,
    EventListener,
    FinishPromptEvent,
    FinishStructureRunEvent,
    TextChunkEvent,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.events.base_event import BaseEvent
    from griptape.structures import Structure


@define
class Stream:
    """A wrapper for Structures that converts `BaseChunkEvent`s into an iterator of TextArtifacts.

    It achieves this by running the Structure in a separate thread, listening for events from the Structure,
    and yielding those events.

    See relevant Stack Overflow post: https://stackoverflow.com/questions/9968592/turn-functions-with-a-callback-into-python-generators

    Attributes:
        structure: The Structure to wrap.
        _event_queue: A queue to hold events from the Structure.
    """

    structure: Structure = field()

    _event_queue: Queue[BaseEvent] = field(default=Factory(lambda: Queue()))

    def run(self, *args) -> Iterator[TextArtifact]:
        t = Thread(target=self._run_structure, args=args)
        t.start()

        action_str = ""
        while True:
            event = self._event_queue.get()
            if isinstance(event, FinishStructureRunEvent):
                break
            elif isinstance(event, FinishPromptEvent):
                yield TextArtifact(value="\n")
            elif isinstance(event, TextChunkEvent):
                yield TextArtifact(value=event.token)
            elif isinstance(event, ActionChunkEvent):
                if event.tag is not None and event.name is not None and event.path is not None:
                    yield TextArtifact(f"{event.name}.{event.tag} ({event.path})")
                if event.partial_input is not None:
                    action_str += event.partial_input
                    try:
                        yield TextArtifact(json.dumps(json.loads(action_str), indent=2))
                        action_str = ""
                    except Exception:
                        pass
        t.join()

    def _run_structure(self, *args) -> None:
        def event_handler(event: BaseEvent) -> None:
            self._event_queue.put(event)

        stream_event_listener = EventListener(
            on_event=event_handler,
            event_types=[BaseChunkEvent, FinishPromptEvent, FinishStructureRunEvent],
        )
        EventBus.add_event_listener(stream_event_listener)

        self.structure.run(*args)

        EventBus.remove_event_listener(stream_event_listener)
