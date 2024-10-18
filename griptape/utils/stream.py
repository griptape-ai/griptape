from __future__ import annotations

import json
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

from attrs import Attribute, Factory, define, field

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
    from collections.abc import Generator, Iterator

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
        from griptape.tasks import PromptTask

        streaming_tasks = [
            task for task in structure.tasks if isinstance(task, PromptTask) and task.prompt_driver.stream
        ]
        if not streaming_tasks:
            raise ValueError("Structure does not have any streaming tasks, enable with stream=True")

    _event_queue: Queue[BaseEvent] = field(default=Factory(lambda: Queue()))

    def run(self, *args) -> Iterator[TextArtifact]:
        t = Thread(target=self._run_structure, args=args)
        t.start()

        action_gen = self._action_print_generator()
        while True:
            event = self._event_queue.get()
            if isinstance(event, FinishStructureRunEvent):
                final_chunk = action_gen.close()
                if final_chunk:
                    yield TextArtifact(value=final_chunk)
                break
            elif isinstance(event, FinishPromptEvent):
                yield TextArtifact(value="\n")
            elif isinstance(event, TextChunkEvent):
                yield TextArtifact(value=str(event))
            elif isinstance(event, ActionChunkEvent):
                action_str = action_gen.send(event)
                if action_str is not None:
                    yield TextArtifact(value=action_str)
                    action_gen = self._action_print_generator()
        t.join()

    def _run_structure(self, *args) -> None:
        def event_handler(event: BaseEvent) -> None:
            self._event_queue.put(event)

        stream_event_listener = EventListener(
            handler=event_handler,
            event_types=[BaseChunkEvent, FinishPromptEvent, FinishStructureRunEvent],
        )
        EventBus.add_event_listener(stream_event_listener)

        self.structure.run(*args)

        EventBus.remove_event_listener(stream_event_listener)

    def _action_print_generator(self) -> Generator[None, ActionChunkEvent, str]:
        event = yield
        try:
            while True:
                next_event = yield
                if next_event.partial_input is not None:
                    if event.partial_input is not None:
                        event.partial_input += next_event.partial_input
                    else:
                        event.partial_input = next_event.partial_input
                if next_event.tag is not None and event.tag is None:
                    event.tag = next_event.tag
                if next_event.name is not None and event.name is None:
                    event.name = next_event.name
                if next_event.path is not None and event.path is None:
                    event.path = next_event.path
                if event.path is not None and event.name is not None and event.tag is not None:
                    return json.dumps(
                        {"tag": event.tag, "name": event.name, "path": event.path, "input": event.partial_input}
                    )
        except GeneratorExit:
            # return the partial input if the generator is closed
            if event.partial_input is not None:
                return event.partial_input
            return ""
