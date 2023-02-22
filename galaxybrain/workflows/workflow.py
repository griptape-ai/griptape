from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field

from galaxybrain.tools import Tool
from galaxybrain.utils import J2
from galaxybrain.rules import Rule
from galaxybrain.workflows.memory import Memory

if TYPE_CHECKING:
    from galaxybrain.drivers import CompletionDriver
    from galaxybrain.workflows import Step, StepOutput


@define
class Workflow:
    completion_driver: CompletionDriver = field(kw_only=True)
    root_step: Optional[Step] = field(default=None)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tools: list[Tool] = field(factory=list, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)

    def __attrs_post_init__(self):
        if self.root_step:
            self.root_step.workflow = self

    def is_empty(self) -> bool:
        return self.root_step is None

    def steps(self):
        all_steps = []
        current_step = self.root_step

        if current_step:
            all_steps.append(current_step)

            while current_step.child is not None:
                current_step = current_step.child

                all_steps.append(current_step)

        return all_steps

    def last_step(self) -> Optional[Step]:
        return self.__last_step_after(self.root_step)

    def add_steps(self, *steps: Step) -> None:
        [self.add_step(s) for s in steps]

    def add_step(self, step: Step) -> Step:
        step.workflow = self

        if self.root_step is None:
            self.root_step = step
        else:
            self.last_step().add_child(step)

        return step

    def add_step_after(self, step: Step, new_step: Step) -> Step:
        new_step.workflow = self

        if step.child:
            new_step.add_child(step.child)
        step.add_child(new_step)

        return new_step

    def start(self) -> Optional[StepOutput]:
        self.__execute_from_step(self.root_step)

        return self.__last_output()

    def resume(self) -> Optional[StepOutput]:
        self.__execute_from_step(self.__next_unfinished_step(self.root_step))

        return self.__last_output()

    def to_prompt_string(self) -> str:
        string_elements = []

        if len(self.tools) > 0:
            string_elements.append(
                J2("tools/tools.j2").render(
                    tools=[
                        J2("tools/tool.j2").render(
                            name=tool.name,
                            description=tool.description,
                            examples=[tool.examples]
                        ) for tool in self.tools
                    ]
                )
            )

        if len(self.rules) > 0:
            string_elements.append(
                J2("rules.j2").render(rules=self.rules)
            )

        string_elements.append(
            self.memory.to_prompt_string()
        )

        return str.join("\n", string_elements)

    def find_tool(self, name: str) -> Optional[Tool]:
        for tool in self.tools:
            if tool.name == name:
                return tool

        return None

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
