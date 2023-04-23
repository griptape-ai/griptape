from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.artifacts import ErrorOutput
from griptape.structures import Structure
from griptape.memory import Memory, Run
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Pipeline(Structure):
    memory: Optional[Memory] = field(default=None, kw_only=True)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.memory:
            self.memory.structure = self

    def first_task(self) -> Optional[BaseTask]:
        return None if self.is_empty() else self.tasks[0]

    def last_task(self) -> Optional[BaseTask]:
        return None if self.is_empty() else self.tasks[-1]

    def finished_tasks(self) -> list[BaseTask]:
        return [s for s in self.tasks if s.is_finished()]

    def add_task(self, task: BaseTask) -> BaseTask:
        if self.last_task():
            self.last_task().add_child(task)
        else:
            task.structure = self

            self.tasks.append(task)

        return task

    def prompt_stack(self, task: BaseTask) -> list[str]:
        final_stack = super().prompt_stack(task)
        task_prompt = J2("prompts/pipeline.j2").render(
            has_memory=self.memory is not None,
            finished_tasks=self.finished_tasks(),
            current_task=task
        )

        if self.memory:
            if self.autoprune_memory:
                last_n = len(self.memory.runs)
                should_prune = True

                while should_prune and last_n > 0:
                    temp_stack = final_stack.copy()
                    temp_stack.append(task_prompt)

                    temp_stack.append(self.memory.to_prompt_string(last_n))

                    if self.prompt_driver.tokenizer.tokens_left(self.stack_to_prompt_string(temp_stack)) > 0:
                        should_prune = False
                    else:
                        last_n -= 1

                if last_n > 0:
                    final_stack.append(self.memory.to_prompt_string(last_n))
            else:
                final_stack.append(self.memory.to_prompt_string())

        final_stack.append(task_prompt)

        return final_stack

    def run(self, *args) -> BaseTask:
        self._execution_args = args

        [task.reset() for task in self.tasks]

        self.__run_from_task(self.first_task())

        if self.memory:
            run = Run(
                input=self.first_task().render_prompt(),
                output=self.last_task().output.value
            )

            self.memory.add_run(run)

        self._execution_args = ()

        return self.last_task()

    def context(self, task: BaseTask) -> dict[str, any]:
        context = super().context(task)

        context.update(
            {
                "input": task.parents[0].output.value if task.parents and task.parents[0].output else None,
                "parent": task.parents[0] if task.parents else None,
                "child": task.children[0] if task.children else None
            }
        )

        return context

    def to_dict(self) -> dict:
        from griptape.schemas import PipelineSchema

        return PipelineSchema().dump(self)

    @classmethod
    def from_dict(cls, pipeline_dict: dict) -> Pipeline:
        from griptape.schemas import PipelineSchema

        return PipelineSchema().load(pipeline_dict)

    @classmethod
    def from_json(cls, pipeline_json: str) -> Pipeline:
        return Pipeline.from_dict(json.loads(pipeline_json))

    def __run_from_task(self, task: Optional[BaseTask]) -> None:
        if task is None:
            return
        else:
            if isinstance(task.execute(), ErrorOutput):
                return
            else:
                self.__run_from_task(next(iter(task.children), None))
