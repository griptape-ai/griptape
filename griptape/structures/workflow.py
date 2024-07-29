from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field
from graphlib import CycleError, TopologicalSorter

from griptape.structures import Structure
from griptape.tasks import BaseTask

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Workflow(Structure):
    _task_id_graph: dict[str, set[str]] = field(factory=dict, kw_only=True, alias="task_id_graph")
    _tasks: list[BaseTask] = field(factory=list, kw_only=True, alias="tasks")

    _last_tasks: set[BaseTask | str] = field(factory=set, init=False, kw_only=True)
    _task_graph: Optional[dict[BaseTask, set[BaseTask]]] = field(default=None, kw_only=True, alias="task_graph")
    _tasks_set: set[BaseTask] = field(factory=set, init=False, kw_only=True)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        if self._tasks:
            self._tasks_set = set(self._tasks)

        if self._task_graph is not None:
            self._from_task_graph()

    @property
    def tasks(self) -> list[BaseTask]:
        return list(self._tasks_set)

    @property
    def task_graph(self) -> dict[BaseTask, set[BaseTask]]:
        return self._task_graph if self._task_graph is not None else {}

    @property
    def task_id_graph(self) -> dict[str, set[str]]:
        return self._task_id_graph

    def context(self, task: BaseTask) -> dict[str, Any]:
        context = super().context(task)

        context.update(
            {
                "parent_outputs": task.parent_outputs,
                "parents_output_text": task.parents_output_text,
                "parents": {parent.id: parent for parent in task.parents},
                "children": {child.id: child for child in task.children},
            },
        )

        return context

    def before_run(self, args: Any) -> None:
        self._validate()
        self._task_graph = self._build_task_graph()
        super().before_run(args)

    def _from_task_graph(self) -> Workflow:
        task_graph = self._task_graph

        for task, parents in task_graph.items():
            task_id = task.id
            if self._task_id_graph.get(task_id) is None:
                self._task_id_graph[task_id] = set()

            for parent in parents:
                parent_id = parent.id
                self._task_id_graph[task_id].add(parent_id)

            self._tasks_set.add(task)

        self._task_graph = None

        return self

    def add_task(
        self,
        task: Optional[BaseTask | str],
        parents: Optional[set[BaseTask | str]] = None,
        children: Optional[set[BaseTask | str]] = None,
        **kwargs,
    ) -> Workflow:
        if task is None:
            raise ValueError("Task must be provided")
        if parents is None:
            parents = set()
        if children is None:
            children = set()
        self._build_task(task, parents=parents, children=children)

        self._last_tasks = {task}
        return self

    def add_tasks(
        self,
        *tasks: BaseTask | str,
        parents: Optional[set[BaseTask | str]] = None,
        children: Optional[set[BaseTask | str]] = None,
        **kwargs,
    ) -> Workflow:
        if not tasks:
            raise ValueError("Tasks must be provided")
        if parents is None:
            parents = set()
        if children is None:
            children = set()

        for task in tasks:
            self._build_task(task, parents=parents, children=children)

        self._last_tasks = set(tasks)  # pright: ignore[assignment]

        return self

    def add_child(self, child: BaseTask | str) -> Workflow:
        if not self._last_tasks:
            raise ValueError("No tasks to add child to")
        for task in self._last_tasks:
            self.add_task(task, children={child})
        self._last_tasks = {child}
        return self

    def add_parent(self, parent: BaseTask | str) -> Workflow:
        if not self._last_tasks:
            raise ValueError("No tasks to add parent to")
        for task in self._last_tasks:
            self.add_task(task, parents={parent})
        self._last_tasks = {parent}
        return self

    def add_parents(self, *parents: BaseTask | str) -> Workflow:
        if not self._last_tasks:
            raise ValueError("No tasks to add parent to")
        for task in self._last_tasks:
            self.add_task(task, parents=set(parents))
        self._last_tasks = set(parents)
        return self

    def add_children(self, *children: BaseTask | str) -> Workflow:
        if not self._last_tasks:
            raise ValueError("No tasks to add children to")
        for task in self._last_tasks:
            self.add_task(task, children=set(children))
        self._last_tasks = set(children)
        return self

    def _build_task(
        self, task: BaseTask | str, parents: set[BaseTask | str], children: set[BaseTask | str]
    ) -> Workflow:
        from griptape.tasks import BaseTask

        if isinstance(task, BaseTask):
            self._tasks_set.add(task)
            task_id = task.id
        else:
            task_id = task

        if self._task_id_graph.get(task_id) is None:
            self._task_id_graph[task_id] = set()

        for parent in parents if parents is not None else set():
            if isinstance(parent, BaseTask):
                parent_id = parent.id
                self._tasks_set.add(parent)
            else:
                parent_id = parent
            if self._task_id_graph.get(parent_id) is None:
                self._task_id_graph[parent_id] = set()
            self._task_id_graph[task_id].add(parent_id)

        for child in children if children is not None else set():
            if isinstance(child, BaseTask):
                child_id = child.id
                self._tasks_set.add(child)
            else:
                child_id = child
            if self._task_id_graph.get(child_id) is None:
                self._task_id_graph[child_id] = set()
            self._task_id_graph[child_id].add(task_id)
        return self

    def _build_task_graph(self) -> dict[BaseTask, set[BaseTask]]:
        self._validate()

        final_task_graph: dict[BaseTask, set[BaseTask]] = {}

        for task_id, parents in self._task_id_graph.items():
            task = None
            final_parents = set()
            for t in self._tasks_set:
                if t.id == task_id:
                    task = t
                    continue
                for parent_id in parents:
                    if t.id == parent_id:
                        final_parents.add(t)
                        continue

            if task is None:
                raise ValueError(f"Task with id {task_id} not found in tasks")
            if len(final_parents) != len(parents):
                raise ValueError(f"Not all children found in tasks for task with id {task_id}")

            if final_task_graph.get(task) is None:
                final_task_graph[task] = set()

            [final_task_graph[task].add(parent) for parent in final_parents]
        return final_task_graph

    def _validate(self) -> None:
        try:
            TopologicalSorter(self.task_id_graph).static_order()
        except CycleError as e:
            raise ValueError("Cycle detected in task graph") from e
