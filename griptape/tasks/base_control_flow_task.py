from __future__ import annotations
from abc import ABC
from attrs import define
from griptape.tasks import BaseTask
from griptape.memory.meta import ControlFlowMetaEntry


@define
class BaseControlFlowTask(BaseTask, ABC):
    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.meta_memory.add_entry(
            ControlFlowMetaEntry(
                input_tasks=[parent.id for parent in self.parents],
                output_tasks=[child.id for child in filter(lambda child: not child.is_finished(), self.children)],
                output=self.output,
            )
        )

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def _cancel_children_rec(self, task: BaseTask, chosen_task: BaseTask) -> None:
        for child in filter(lambda child: child != chosen_task, task.children):
            if all(parent.is_complete() for parent in filter(lambda parent: parent != task, child.parents)):
                child.state = BaseTask.State.CANCELLED
                self._cancel_children_rec(child, chosen_task)

    def _get_task(self, task: str | BaseTask) -> BaseTask:
        return self.structure.find_task(task) if isinstance(task, str) else task
