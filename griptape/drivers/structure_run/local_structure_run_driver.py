from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver
from griptape.events import EventBus

if TYPE_CHECKING:
    from griptape.events import EventListener
    from griptape.structures import Structure


@define
class LocalStructureRunDriver(BaseStructureRunDriver):
    """Runs a structure locally.

    Attributes:
        structure_factory_fn: A function that returns a Structure.
        event_listeners: A list of Event Listeners to add to the Event Bus for the Structure's run.
    """

    structure_factory_fn: Callable[[], Structure] = field(kw_only=True)
    event_listeners: list[EventListener] = field(factory=list, kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact:
        # Save the current environment and event listeners so we can restore them after running the structure.
        old_env = os.environ.copy()
        old_event_listeners = EventBus.event_listeners.copy()
        EventBus.clear_event_listeners()

        try:
            os.environ.update(self.env)
            EventBus.set_event_listeners(self.event_listeners)

            structure_factory_fn = self.structure_factory_fn().run(*[arg.value for arg in args])
        finally:
            EventBus.set_event_listeners(old_event_listeners)
            os.environ.clear()
            os.environ.update(old_env)

        if structure_factory_fn.output_task.output is not None:
            return structure_factory_fn.output_task.output
        else:
            return InfoArtifact("No output found in response")
