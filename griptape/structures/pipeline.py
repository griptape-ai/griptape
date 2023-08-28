from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
from attr import define
from griptape.artifacts import ErrorArtifact
from griptape.memory.structure import Run
from griptape.structures import Structure

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Pipeline(Structure):
    def first_task(self) -> Optional[BaseTask]:
        return self.tasks[0] if self.tasks else None

    def last_task(self) -> Optional[BaseTask]:
        return self.tasks[-1] if self.tasks else None

    def finished_tasks(self) -> list[BaseTask]:
        return [s for s in self.tasks if s.is_finished()]

    def __add__(self, other: Union[BaseTask, list[BaseTask]]) -> list[BaseTask]:
        return [self.add_task(o) for o in other] if isinstance(other, list) else self + [other]

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)

        if self.last_task():
            self.last_task().add_child(task)
        else:
            task.structure = self

            self.tasks.append(task)

        return task

    def run(self, *args) -> BaseTask:
        self._execution_args = args

        [task.reset() for task in self.tasks]

        self.__run_from_task(self.first_task())

        if self.memory:
            run = Run(
                input=self.first_task().input.to_text(),
                output=self.last_task().output.to_text()
            )

            self.memory.add_run(run)

        self._execution_args = ()

        return self.last_task()

    def context(self, task: BaseTask) -> dict[str, any]:
        context = super().context(task)

        context.update(
            {
                "parent_output": task.parents[0].output.to_text() if task.parents and task.parents[0].output else None,
                "parent": task.parents[0] if task.parents else None,
                "child": task.children[0] if task.children else None
            }
        )

        return context

    def __run_from_task(self, task: Optional[BaseTask]) -> None:
        if task is None:
            return
        else:
            if isinstance(task.execute(), ErrorArtifact):
                return
            else:
                self.__run_from_task(next(iter(task.children), None))
