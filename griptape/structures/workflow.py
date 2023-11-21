from __future__ import annotations
import concurrent.futures as futures
from graphlib import TopologicalSorter
from typing import Any
from attr import define, field, Factory
from griptape.artifacts import ErrorArtifact
from griptape.structures import Structure
from griptape.tasks import BaseTask
from griptape.memory.structure import Run


@define
class Workflow(Structure):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        if self.output_task:
            self.output_task.child_ids.append(task.id)
            task.parent_ids.append(self.output_task.id)

        self.tasks.append(task)

        return task

    def insert_tasks(
        self,
        parent_tasks: BaseTask | list[BaseTask],
        tasks: BaseTask | list[BaseTask],
        child_tasks: BaseTask | list[BaseTask],
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
            self.insert_task(parent_tasks, task, child_tasks, preserve_relationship)

        return tasks

    def insert_task(
        self,
        parent_tasks: list[BaseTask],
        task: BaseTask,
        child_tasks: list[BaseTask],
        preserve_relationship: bool = False,
    ) -> BaseTask:
        task.preprocess(self)

        for child_task in child_tasks:
            # Link the new task to the child task
            if child_task.id not in task.child_ids:
                task.child_ids.append(child_task.id)
            if task.id not in child_task.parent_ids:
                child_task.parent_ids.append(task.id)

        if not preserve_relationship:
            for parent_task in parent_tasks:
                for child_task in child_tasks:
                    # Remove the old parent/child relationship
                    if child_task.id in parent_task.child_ids:
                        parent_task.child_ids.remove(child_task.id)
                    if parent_task.id in child_task.parent_ids:
                        child_task.parent_ids.remove(parent_task.id)

        for parent_task in parent_tasks:
            # Link the new task to the parent task
            if parent_task.id not in task.parent_ids:
                task.parent_ids.append(parent_task.id)
            if task.id not in parent_task.child_ids:
                parent_task.child_ids.append(task.id)

            parent_index = self.tasks.index(parent_task)
            self.tasks.insert(parent_index + 1, task)

        return task

    def try_run(self, *args) -> Workflow:
        self._execution_args = args
        ordered_tasks = self.order_tasks()
        exit_loop = False

        while not self.is_finished() and not exit_loop:
            futures_list = {}

            for task in ordered_tasks:
                if task.can_execute():
                    future = self.futures_executor.submit(task.execute)
                    futures_list[future] = task

            # Wait for all tasks to complete
            for future in futures.as_completed(futures_list):
                if isinstance(future.result(), ErrorArtifact):
                    exit_loop = True

                    break

        if self.conversation_memory:
            run = Run(input=self.input_task.input.to_text(), output=self.output_task.output.to_text())

            self.conversation_memory.add_run(run)

        self._execution_args = ()

        return self

    def context(self, task: BaseTask) -> dict[str, Any]:
        context = super().context(task)

        context.update(
            {
                "parent_outputs": {
                    parent.id: parent.output.to_text() if parent.output else "" for parent in task.parents
                },
                "parents": {parent.id: parent for parent in task.parents},
                "children": {child.id: child for child in task.children},
            }
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
