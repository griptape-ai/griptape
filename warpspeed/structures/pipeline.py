from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from warpspeed.artifacts import ErrorOutput
from warpspeed.schemas import PipelineSchema
from warpspeed.structures import Structure
from warpspeed.memory import PipelineMemory, PipelineRun
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.steps import Step


@define
class Pipeline(Structure):
    memory: Optional[PipelineMemory] = field(default=None, kw_only=True)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.memory:
            self.memory.pipeline = self

    def first_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[0]

    def last_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[-1]

    def finished_steps(self) -> list[Step]:
        return [s for s in self.steps if s.is_finished()]

    def add_step(self, step: Step) -> Step:
        if self.last_step():
            self.last_step().add_child(step)
        else:
            step.structure = self

            self.steps.append(step)

        return step

    def prompt_stack(self, step: Step) -> list[str]:
        stack = super().prompt_stack(step)

        if self.memory:
            stack.append(
                self.memory.to_prompt_string()
            )

        stack.append(
            J2("prompts/pipeline.j2").render(
                has_memory=self.memory is not None,
                finished_steps=self.finished_steps(),
                current_step=step
            )
        )

        return stack

    def run(self, *args) -> Step:
        self._execution_args = args

        [step.reset() for step in self.steps]

        self.__run_from_step(self.first_step())

        if self.memory:
            run_context = PipelineRun(
                prompt=self.first_step().render_prompt(),
                output=self.last_step().output
            )

            self.memory.add_run(run_context)

        self._execution_args = ()

        return self.last_step()

    def context(self, step: Step) -> dict[str, any]:
        context = super().context(step)

        context.update(
            {
                "input": step.parents[0].output.value if step.parents and step.parents[0].output else None,
                "parent": step.parents[0] if step.parents else None,
                "child": step.children[0] if step.children else None
            }
        )

        return context

    def to_dict(self) -> dict:
        return PipelineSchema().dump(self)

    @classmethod
    def from_dict(cls, workflow_dict: dict) -> Pipeline:
        return PipelineSchema().load(workflow_dict)

    @classmethod
    def from_json(cls, workflow_json: str) -> Pipeline:
        return Pipeline.from_dict(json.loads(workflow_json))

    def __run_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            if isinstance(step.execute(), ErrorOutput):
                return
            else:
                self.__run_from_step(next(iter(step.children), None))
