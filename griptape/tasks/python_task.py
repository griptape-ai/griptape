from __future__ import annotations
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tasks import BaseTextInputTask
from typing import Callable


@define
class CallableTask(BaseTextInputTask):
    run_fn: Callable[[CallableTask], BaseArtifact] = field(kw_only=True)

    def run(self) -> BaseArtifact:
        try:
            return self.run_fn(self)
        except Exception as e:
            return ErrorArtifact(f"error during Python Task execution: {e}")
