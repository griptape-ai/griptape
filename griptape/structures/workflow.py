from __future__ import annotations
import concurrent.futures as futures
from graphlib import TopologicalSorter
from typing import Union
from attr import define, field, Factory
from griptape.artifacts import ErrorArtifact
from griptape.structures import Structure
from griptape.tasks import BaseTask


@define
class Workflow(Structure):
    futures_executor: futures.Executor = field(
        default=Factory(lambda: futures.ThreadPoolExecutor()),
        kw_only=True
    )

    def __add__(self, other: Union[BaseTask, list[BaseTask]]) -> BaseTask:
        return [self.add_task(o) for o in other] if isinstance(other, list) else self + [other]

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        self.tasks.append(task)

        return task

    def run(self, *args) -> list[BaseTask]:
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

        self._execution_args = ()

        return self.output_tasks()

    def context(self, task: BaseTask) -> dict[str, any]:
        context = super().context(task)

        context.update(
            {
                "parent_outputs": {parent.id: parent.output.to_text() if parent.output else "" for parent in task.parents},
                "parents": {parent.id: parent for parent in task.parents},
                "children": {child.id: child for child in task.children}
            }
        )

        return context

    def output_tasks(self) -> list[BaseTask]:
        return [task for task in self.tasks if not task.children]

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
