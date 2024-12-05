from __future__ import annotations

from typing import Callable, Union

from attrs import define, field

from griptape.artifacts import InfoArtifact, ListArtifact
from griptape.tasks import BaseTask, CodeExecutionTask


@define
class BranchTask(CodeExecutionTask):
    on_run: Callable[[BranchTask], Union[InfoArtifact, ListArtifact[InfoArtifact]]] = field(kw_only=True)

    def try_run(self) -> InfoArtifact | ListArtifact[InfoArtifact]:
        result = self.on_run(self)

        if isinstance(result, ListArtifact):
            branch_task_ids = {artifact.value for artifact in result}
        else:
            branch_task_ids = {result.value}

        if not all(branch_task_id in self.child_ids for branch_task_id in branch_task_ids):
            raise ValueError(f"Branch task returned invalid child task id {branch_task_ids}")

        if self.structure is not None:
            children_to_skip = [child for child in self.children if child.id not in branch_task_ids]
            for child in children_to_skip:
                child.state = BaseTask.State.SKIPPED

        return result
