from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.common import observable
from griptape.configs import Defaults
from griptape.structures import Structure
from griptape.tasks.branch_task import BranchTask

if TYPE_CHECKING:
    from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class StateMachine(Structure):
    @property
    def input_task(self) -> Optional[BaseTask]:
        return next((task for task in self.tasks if task.meta.get("start", False)), None)

    @property
    def output_task(self) -> Optional[BaseTask]:
        return next((task for task in self.tasks if task.meta.get("end", False)), None)

    current_task: BaseTask = field(init=False, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if self.input_task is not None:
            self.current_task = self.input_task

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)
        self._tasks.append(task)

        return task

    def is_finished(self) -> bool:
        return self.current_task.meta.get("end", False)

    def context(self, task: BaseTask) -> dict[str, Any]:
        context = super().context(task)

        context.update(
            {
                "task_outputs": self.task_outputs,
                "parent_outputs": task.parent_outputs,
                "parents_output_text": task.parents_output_text,
                "parents": {parent.id: parent for parent in task.parents},
                "children": {child.id: child for child in task.children},
            },
        )

        return context

    def resolve_relationships(self) -> None:
        super().resolve_relationships()

        for task in self.tasks:
            if not isinstance(task, BranchTask) and len(task.child_ids) > 1:
                raise ValueError(f"Task {task.id} cannot have more than one child.")

    @observable
    def try_run(self, *args) -> StateMachine:
        while not self.is_finished():
            result = self.current_task.run(*args)
            if isinstance(result, ErrorArtifact) and self.fail_fast:
                break

            if isinstance(self.current_task, BranchTask):
                self.current_task = self.find_task(result.value)
            else:
                self.current_task = self.current_task.children[0]

        return self
