from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field
from skatepark.artifacts import ErrorOutput
from skatepark.structures import Structure
from skatepark.memory import PipelineMemory, PipelineRun
from skatepark.utils import J2

if TYPE_CHECKING:
    from skatepark.steps import Step


@define
class Pipeline(Structure):
    memory: Optional[PipelineMemory] = field(default=None, kw_only=True)
    autoprune_memory: bool = field(default=True, kw_only=True)

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
        final_stack = super().prompt_stack(step)
        step_prompt = J2("prompts/pipeline.j2").render(
            has_memory=self.memory is not None,
            finished_steps=self.finished_steps(),
            current_step=step
        )

        if self.memory:
            if self.autoprune_memory:
                last_n = len(self.memory.runs)
                should_prune = True

                while should_prune and last_n > 0:
                    temp_stack = final_stack.copy()
                    temp_stack.append(step_prompt)

                    temp_stack.append(self.memory.to_prompt_string(last_n))

                    if self.prompt_driver.tokenizer.tokens_left(self.stack_to_prompt_string(temp_stack)) > 0:
                        should_prune = False
                    else:
                        last_n -= 1

                if last_n > 0:
                    final_stack.append(self.memory.to_prompt_string(last_n))
            else:
                final_stack.append(self.memory.to_prompt_string())

        final_stack.append(step_prompt)

        return final_stack

    def run(self, *args) -> Step:
        self._execution_args = args

        [step.reset() for step in self.steps]

        self.__run_from_step(self.first_step())

        if self.memory:
            run = PipelineRun(
                input=self.first_step().render_prompt(),
                output=self.last_step().output.value
            )

            self.memory.add_run(run)

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
        from skatepark.schemas import PipelineSchema

        return PipelineSchema().dump(self)

    @classmethod
    def from_dict(cls, pipeline_dict: dict) -> Pipeline:
        from skatepark.schemas import PipelineSchema

        return PipelineSchema().load(pipeline_dict)

    @classmethod
    def from_json(cls, pipeline_json: str) -> Pipeline:
        return Pipeline.from_dict(json.loads(pipeline_json))

    def __run_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            if isinstance(step.execute(), ErrorOutput):
                return
            else:
                self.__run_from_step(next(iter(step.children), None))
