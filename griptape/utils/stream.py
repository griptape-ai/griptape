from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.events import (
    ActionChunkEvent,
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
    """A wrapper for Structures filters Events relevant to text output and converts them to TextArtifacts.

    Attributes:
        structure: The Structure to wrap.
    """

    structure: Structure = field()
    event_types: list[type[BaseEvent]] = field(
        default=Factory(lambda: [TextChunkEvent, ActionChunkEvent, FinishPromptEvent, FinishStructureRunEvent])
    )

    def run(self, *args) -> Iterator[TextArtifact]:
        action_str = ""

        for event in self.structure.run_stream(*args, event_types=self.event_types):
            if isinstance(event, FinishPromptEvent):
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
