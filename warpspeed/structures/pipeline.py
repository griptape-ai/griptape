from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from warpspeed.artifacts import ErrorOutput
from warpspeed.schemas import PipelineSchema
from warpspeed.structures import Structure
from warpspeed.memory import Memory
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.steps import Step


@define
class Pipeline(Structure):
    memory: Optional[Memory] = field(default=None, kw_only=True)

    def first_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[0]

    def last_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[-1]

    def add_step(self, step: Step) -> Step:
        if self.last_step():
            self.last_step().add_child(step)
        else:
            step.structure = self

            self.steps.append(step)

        return step

    def before_run(self, step: Step) -> None:
        Structure.before_run(self, step)

        if self.memory:
            self.memory.before_run(step)

    def after_run(self, step: Step) -> None:
        Structure.after_run(self, step)

        if self.memory:
            self.memory.after_run(step)

    def prompt_stack(self, step: Step) -> list[str]:
        stack = Structure.prompt_stack(self, step)

        if self.memory:
            stack.append(
                self.memory.to_prompt_string()
            )
        else:
            stack.append(
                J2("prompts/structure.j2").render(
                    step=step
                )
            )

        return stack

    def run(self) -> Step:
        [step.reset() for step in self.steps]

        self.__execute_from_step(self.first_step())

        return self.last_step()

    def resume(self) -> Step:
        self.__execute_from_step(self.__next_unfinished_step(self.first_step()))

        return self.last_step()

    def to_dict(self) -> dict:
        return PipelineSchema().dump(self)

    @classmethod
    def from_dict(cls, workflow_dict: dict) -> Pipeline:
        return PipelineSchema().load(workflow_dict)

    @classmethod
    def from_json(cls, workflow_json: str) -> Pipeline:
        return Pipeline.from_dict(json.loads(workflow_json))

    def __last_step_after(self, step: Optional[Step]) -> Optional[Step]:
        child = next(iter(step.children), None)

        if step is None:
            return None
        elif child:
            return self.__last_step_after(child)
        else:
            return step

    def __execute_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            if isinstance(step.execute(), ErrorOutput):
                return
            else:
                self.__execute_from_step(next(iter(step.children), None))

    def __next_unfinished_step(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.is_finished():
            return self.__next_unfinished_step(next(iter(step.children), None))
        else:
            return step
