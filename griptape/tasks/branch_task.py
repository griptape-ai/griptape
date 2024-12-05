from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.tasks import CodeExecutionTask

if TYPE_CHECKING:
    from griptape.artifacts.info_artifact import InfoArtifact


@define
class BranchTask(CodeExecutionTask):
    on_run: Callable[[BranchTask], InfoArtifact] = field(kw_only=True)

    def try_run(self) -> InfoArtifact:
        result = self.on_run(self)

        if result.value not in self.child_ids:
            raise ValueError(f"Branch result {result.value} not in child_ids {self.child_ids}")

        return result
