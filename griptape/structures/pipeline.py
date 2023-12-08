from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from attr import define
from griptape.artifacts import ErrorArtifact
from griptape.memory.structure import Run
from griptape.structures import Structure

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Pipeline(Structure):
    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        if self.output_task:
            self.output_task.child_ids.append(task.id)
            task.parent_ids.append(self.output_task.id)

        self.tasks.append(task)

        return task

    def insert_task(self, parent_task: BaseTask, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        if parent_task.children:
            child_task = parent_task.children[0]

            task.child_ids.append(child_task.id)
            child_task.parent_ids.append(task.id)

            child_task.parent_ids.remove(parent_task.id)
            parent_task.child_ids.remove(child_task.id)

        task.parent_ids.append(parent_task.id)
        parent_task.child_ids.append(task.id)

        parent_index = self.tasks.index(parent_task)
        self.tasks.insert(parent_index + 1, task)

        return task

    def try_run(self, *args) -> Pipeline:
        self._execution_args = args

        [task.reset() for task in self.tasks]

        self.__run_from_task(self.input_task)

        if self.conversation_memory:
            run = Run(input=self.input_task.input.to_text(), output=self.output_task.output.to_text())

            self.conversation_memory.add_run(run)

        self._execution_args = ()

        return self

    def context(self, task: BaseTask) -> dict[str, Any]:
        context = super().context(task)

        context.update(
            {
                "parent_output": task.parents[0].output.to_text() if task.parents and task.parents[0].output else None,
                "parent": task.parents[0] if task.parents else None,
                "child": task.children[0] if task.children else None,
            }
        )

        return context

    def __run_from_task(self, task: BaseTask | None) -> None:
        if task is None:
            return
        else:
            if isinstance(task.execute(), ErrorArtifact):
                return
            else:
                self.__run_from_task(next(iter(task.children), None))
