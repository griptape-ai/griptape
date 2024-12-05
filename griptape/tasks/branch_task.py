from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import EmptyArtifact, InfoArtifact
from griptape.tasks import CodeExecutionTask


@define
class BranchTask(CodeExecutionTask):
    on_run: Callable[[BranchTask], InfoArtifact] = field(kw_only=True)

    def try_run(self) -> InfoArtifact | EmptyArtifact:
        result = self.on_run(self)

        if isinstance(result, InfoArtifact) and result.value not in self.child_ids:
            raise ValueError(f"Branch result {result.value} not in child_ids {self.child_ids}")

        return result
