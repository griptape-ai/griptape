from __future__ import annotations

import os
from contextlib import ExitStack
from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver

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
        old_env = os.environ.copy()
        try:
            os.environ.update(self.env)

            with ExitStack() as stack:
                for event_listener in self.event_listeners:
                    stack.enter_context(event_listener)
                structure_factory_fn = self.structure_factory_fn().run(*[arg.value for arg in args])
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        if structure_factory_fn.output_task.output is not None:
            return structure_factory_fn.output_task.output
        else:
            return InfoArtifact("No output found in response")
