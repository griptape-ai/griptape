from __future__ import annotations

import concurrent.futures as futures
from typing import TYPE_CHECKING, Any, Optional

from attrs import define
from graphlib import TopologicalSorter

from typing import Any, Optional
from attrs import define
from griptape.artifacts import ErrorArtifact
from griptape.common import observable
from griptape.memory.structure import Run
from griptape.mixins import FuturesExecutorMixin
from griptape.structures import Structure

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Workflow(Structure):
    @property
    def input_task(self) -> Optional[BaseTask]:
        return self.order_tasks()[0] if self.tasks else None

    @property
    def output_task(self) -> Optional[BaseTask]:
        return self.order_tasks()[-1] if self.tasks else None

    def add_task(self, task: BaseTask) -> BaseTask:
        if (existing_task := self.try_find_task(task.id)) is not None:
            return existing_task

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
                    future = self.futures_executor.submit(task.execute)
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
