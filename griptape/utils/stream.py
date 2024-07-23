from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

from attrs import Attribute, Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.events.completion_chunk_event import CompletionChunkEvent
from griptape.events.event_listener import EventListener
from griptape.events.finish_prompt_event import FinishPromptEvent
from griptape.events.finish_structure_run_event import FinishStructureRunEvent

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.events.base_event import BaseEvent
    from griptape.structures import Structure


@define
class Stream:
    """A wrapper for Structures that converts `CompletionChunkEvent`s into an iterator of TextArtifacts.

    It achieves this by running the Structure in a separate thread, listening for events from the Structure,
    and yielding those events.

    See relevant Stack Overflow post: https://stackoverflow.com/questions/9968592/turn-functions-with-a-callback-into-python-generators

    Attributes:
        structure: The Structure to wrap.
        _event_queue: A queue to hold events from the Structure.
    """

    structure: Structure = field()

    @structure.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_structure(self, _: Attribute, structure: Structure) -> None:
        if not structure.config.prompt_driver.stream:
            raise ValueError("prompt driver does not have streaming enabled, enable with stream=True")

    _event_queue: Queue[BaseEvent] = field(default=Factory(lambda: Queue()))

    def run(self, *args) -> Iterator[TextArtifact]:
        t = Thread(target=self._run_structure, args=args)
        t.start()

        while True:
            event = self._event_queue.get()
            if isinstance(event, FinishStructureRunEvent):
                break
            elif isinstance(event, FinishPromptEvent):
                yield TextArtifact(value="\n")
            elif isinstance(event, CompletionChunkEvent):
                yield TextArtifact(value=event.token)
        t.join()

    def _run_structure(self, *args) -> None:
        def event_handler(event: BaseEvent) -> None:
            self._event_queue.put(event)

        stream_event_listener = EventListener(
            handler=event_handler,
            event_types=[CompletionChunkEvent, FinishPromptEvent, FinishStructureRunEvent],
        )
        self.structure.add_event_listener(stream_event_listener)

        self.structure.run(*args)

        self.structure.remove_event_listener(stream_event_listener)
