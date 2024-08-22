from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class CodeExecutionTask(BaseTextInputTask):
    run_fn: Callable[[CodeExecutionTask], BaseArtifact] = field(kw_only=True)

    def run(self) -> BaseArtifact:
        return self.run_fn(self)
