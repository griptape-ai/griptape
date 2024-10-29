from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class CodeExecutionTask(BaseTextInputTask):
    on_run: Callable[[CodeExecutionTask], BaseArtifact] = field(kw_only=True)

    def try_run(self) -> BaseArtifact:
        return self.on_run(self)
