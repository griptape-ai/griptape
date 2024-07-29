from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.structures import Structure

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Pipeline(Structure):
    _tasks: list[BaseTask] = field(factory=list, kw_only=True, alias="tasks")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

    @property
    def tasks(self) -> list[BaseTask]:
        return self._tasks

    @property
    def task_graph(self) -> dict[BaseTask, set[BaseTask]]:
        task_graph = {}
        for i, task in enumerate(self._tasks):
            if i == 0:
                task_graph[task] = set()
                continue
            if i < len(self._tasks):
                task_graph[task] = {self._tasks[i - 1]}
        return task_graph

    def context(self, task: BaseTask) -> dict[str, Any]:
        context = super().context(task)

        context.update(
            {
                "parent_output": task.parent_outputs,
                "parent_output_text": task.parents_output_text,
                "parent": {parent.id: parent for parent in task.parents},
                "child": {child.id: child for child in task.children},
            }
        )

        return context

    def add_task(
        self,
        task: Optional[BaseTask],
        index: int = -1,
        parent: Optional[BaseTask | str] = None,
        child: Optional[BaseTask | str] = None,
        **kwargs,
    ) -> Pipeline:
        if task is None:
            raise ValueError("Task must be provided.")
        try:
            parent_task = self.find_task(parent) if isinstance(parent, str) else parent
            child_task = self.find_task(child) if isinstance(child, str) else child

            if (
                parent_task is not None
                and child_task is not None
                and self._tasks.index(parent_task) - self._tasks.index(child_task) != -1
            ):
                raise ValueError("Parent and child tasks must be adjacent.")
            if parent_task is not None:
                self._tasks.insert(self._tasks.index(parent_task) + 1, task)
                return self
            elif child_task is not None:
                self._tasks.insert(self._tasks.index(child_task), task)
                return self
        except ValueError as e:
            raise ValueError("Parent or child task not found in the pipeline.") from e

        if index <= -1 or index >= len(self._tasks):
            index = len(self._tasks)

        task.preprocess(self)
        self._tasks.insert(index, task)

        return self
