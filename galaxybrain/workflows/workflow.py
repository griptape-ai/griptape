from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.schemas import WorkflowSchema
from galaxybrain.utils import J2
from galaxybrain.rules import Rule
from galaxybrain.workflows.memory import Memory
from galaxybrain.drivers import OpenAiPromptDriver

if TYPE_CHECKING:
    from galaxybrain.drivers import PromptDriver
    from galaxybrain.artifacts import StepOutput
    from galaxybrain.workflows import Step, ToolStep, ToolkitStep


@define
class Workflow:
    prompt_driver: PromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)
    steps: list[Step] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def find_step(self, step_id: str) -> Optional[Step]:
        return next((step for step in self.steps if step.id == step_id), None)

    def first_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[0]

    def last_step(self) -> Optional[Step]:
        return None if self.is_empty() else self.steps[-1]

    def add_steps(self, *steps: Step) -> None:
        [self.add_step(s) for s in steps]

    def add_step(self, step: Step) -> Step:
        step.workflow = self

        if self.last_step():
            self.last_step().add_child(step)

        self.steps.append(step)

        return step

    def add_step_after(self, step: Step, new_step: Step) -> Step:
        new_step.workflow = self

        if step.child:
            new_step.add_child(step.child)
        step.add_child(new_step)

        self.steps.append(new_step)

        return new_step

    def start(self) -> Optional[StepOutput]:
        self.__execute_from_step(self.first_step())

        return self.__last_output()

    def resume(self) -> Optional[StepOutput]:
        self.__execute_from_step(self.__next_unfinished_step(self.first_step()))

        return self.__last_output()

    def to_prompt_string(self) -> str:
        from galaxybrain.workflows import ToolStep, ToolkitStep

        step = self.__next_unfinished_step(self.first_step())

        if isinstance(step, ToolStep):
            tools = [step.tool]
        elif isinstance(step, ToolkitStep):
            tools = step.tools
        else:
            tools = []

        prompt_elements = [
            J2("prompts/context.j2").render(
                rules=self.rules,
                tool_names=str.join(", ", [tool.name for tool in tools]),
                tools=[J2("prompts/tool.j2").render(tool=tool) for tool in tools]
            ),
            self.memory.to_prompt_string()
        ]

        return str.join("\n", prompt_elements)

    def token_count(self) -> int:
        return self.prompt_driver.tokenizer.token_count(
            self.to_prompt_string()
        )

    def to_dict(self) -> dict:
        return WorkflowSchema().dump(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, workflow_dict: dict) -> Workflow:
        return WorkflowSchema().load(workflow_dict)

    @classmethod
    def from_json(cls, workflow_json: str) -> Workflow:
        return Workflow.from_dict(json.loads(workflow_json))

    def __last_output(self) -> Optional[StepOutput]:
        if self.is_empty():
            return None
        else:
            return self.last_step().output

    def __last_step_after(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.child:
            return self.__last_step_after(step.child)
        else:
            return step

    def __execute_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            step.execute()

            self.__execute_from_step(step.child)

    def __next_unfinished_step(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.is_finished():
            return self.__next_unfinished_step(step.child)
        else:
            return step
