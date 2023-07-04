from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from attr import define, field, Factory
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.memory.structure import SubtaskRun

@define
class Run:
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    input: str = field(kw_only=True)
    output: str = field(kw_only=True)
    subtask_runs: list[SubtaskRun] = field(default=[], kw_only=True)

    def render(self) -> str:
        return J2("prompts/run.j2").render(
            run=self,
            subtask_runs=self.subtask_runs
        )
