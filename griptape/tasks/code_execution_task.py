from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tasks import BaseTextInputTask


@define
class CodeExecutionTask(BaseTextInputTask):
    run_fn: Callable[[CodeExecutionTask], BaseArtifact] = field(kw_only=True)

    def run(self) -> BaseArtifact:
        try:
            return self.run_fn(self)
        except Exception as e:
            return ErrorArtifact(f"error during Code Execution Task: {e}")
