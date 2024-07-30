from __future__ import annotations

import concurrent.futures as futures
from typing import TYPE_CHECKING, Any, Callable, Optional

from attrs import Factory, define, field
from graphlib import TopologicalSorter

from griptape.artifacts import ErrorArtifact
from griptape.common import observable
from griptape.memory.structure import Run
from griptape.structures import Structure

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Workflow(Structure):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
        kw_only=True,
    )

    @property
    def output_task(self) -> Optional[BaseTask]:
        return self.order_tasks()[-1] if self.tasks else None

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        self.tasks.append(task)

        return task

    def insert_tasks(
        self,
        parent_tasks: BaseTask | list[BaseTask],
        tasks: BaseTask | list[BaseTask],
        child_tasks: BaseTask | list[BaseTask],
        *,
        preserve_relationship: bool = False,
    ) -> list[BaseTask]:
        """Insert tasks between parent and child tasks in the workflow.

        Args:
            parent_tasks: The tasks that will be the parents of the new tasks.
            tasks: The tasks to insert between the parent and child tasks.
            child_tasks: The tasks that will be the children of the new tasks.
            preserve_relationship: Whether to preserve the parent/child relationship when inserting between parent and child tasks.
        """
        if not isinstance(parent_tasks, list):
            parent_tasks = [parent_tasks]
        if not isinstance(tasks, list):
            tasks = [tasks]
        if not isinstance(child_tasks, list):
            child_tasks = [child_tasks]

        for task in tasks:
            self.insert_task(parent_tasks, task, child_tasks, preserve_relationship=preserve_relationship)

        return tasks

    def insert_task(
        self,
        parent_tasks: list[BaseTask],
        task: BaseTask,
        child_tasks: list[BaseTask],
        *,
        preserve_relationship: bool = False,
    ) -> BaseTask:
        task.preprocess(self)

        self.__link_task_to_children(task, child_tasks)

        if not preserve_relationship:
            self.__remove_old_parent_child_relationships(parent_tasks, child_tasks)

        last_parent_index = self.__link_task_to_parents(task, parent_tasks)

        # Insert the new task once, just after the last parent task
        self.tasks.insert(last_parent_index + 1, task)

        return task

    @observable
    def try_run(self, *args) -> Workflow:
        exit_loop = False

        while not self.is_finished() and not exit_loop:
            futures_list = {}
            ordered_tasks = self.order_tasks()

            for task in ordered_tasks:
                if task.can_execute():
                    future = self.futures_executor_fn().submit(task.execute)
                    futures_list[future] = task

            # Wait for all tasks to complete
            for future in futures.as_completed(futures_list):
                if isinstance(future.result(), ErrorArtifact) and self.fail_fast:
                    exit_loop = True

                    break

        if self.conversation_memory and self.output is not None:
            run = Run(input=self.input_task.input, output=self.output)

            self.conversation_memory.add_run(run)

        return self

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

    def to_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}

        for key_task in self.tasks:
            graph[key_task.id] = set()

            for value_task in self.tasks:
                if key_task.id in value_task.child_ids:
                    graph[key_task.id].add(value_task.id)

        return graph

    def order_tasks(self) -> list[BaseTask]:
        return [self.find_task(task_id) for task_id in TopologicalSorter(self.to_graph()).static_order()]

    def __link_task_to_children(self, task: BaseTask, child_tasks: list[BaseTask]) -> None:
        for child_task in child_tasks:
            # Link the new task to the child task
            if child_task.id not in task.child_ids:
                task.child_ids.append(child_task.id)
            if task.id not in child_task.parent_ids:
                child_task.parent_ids.append(task.id)

    def __remove_old_parent_child_relationships(
        self,
        parent_tasks: list[BaseTask],
        child_tasks: list[BaseTask],
    ) -> None:
        for parent_task in parent_tasks:
            for child_task in child_tasks:
                # Remove the old parent/child relationship
                if child_task.id in parent_task.child_ids:
                    parent_task.child_ids.remove(child_task.id)
                if parent_task.id in child_task.parent_ids:
                    child_task.parent_ids.remove(parent_task.id)

    def __link_task_to_parents(self, task: BaseTask, parent_tasks: list[BaseTask]) -> int:
        last_parent_index = -1
        for parent_task in parent_tasks:
            # Link the new task to the parent task
            if parent_task.id not in task.parent_ids:
                task.parent_ids.append(parent_task.id)
            if task.id not in parent_task.child_ids:
                parent_task.child_ids.append(task.id)

            try:
                parent_index = self.tasks.index(parent_task)
            except ValueError as exc:
                raise ValueError(f"Parent task {parent_task.id} not found in workflow.") from exc
            else:
                if parent_index > last_parent_index:
                    last_parent_index = parent_index

        return last_parent_index
