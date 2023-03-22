from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from warpspeed.tools import Tool
from warpspeed.utils import J2
from warpspeed.steps import PromptStep
from warpspeed.artifacts import TextOutput, ErrorOutput

if TYPE_CHECKING:
    from warpspeed.steps import ToolSubstep


@define
class BaseToolStep(PromptStep, ABC):
    DEFAULT_MAX_SUBSTEPS = 20

    max_substeps: int = field(default=DEFAULT_MAX_SUBSTEPS, kw_only=True)
    _substeps: list[ToolSubstep] = field(factory=list)

    def run(self) -> TextOutput:
        from warpspeed.steps import ToolSubstep

        self._substeps.clear()

        substep = self.add_substep(
            ToolSubstep(
                self.active_driver().run(value=self.structure.to_prompt_string(self)).value
            )
        )

        while True:
            if substep.output is None:
                if len(self._substeps) >= self.max_substeps:
                    substep.output = ErrorOutput(
                        f"Exceeded maximum tool execution limit of {self.max_substeps} per step",
                        step=self
                    )
                elif substep.tool_name is None:
                    # handle case when the LLM failed to follow the ReAct prompt and didn't return a proper action
                    substep.output = TextOutput(substep.prompt_template)
                else:
                    substep.before_run()
                    substep.run()
                    substep.after_run()

                    substep = self.add_substep(
                        ToolSubstep(
                            self.active_driver().run(value=self.structure.to_prompt_string(self)).value
                        )
                    )
            else:
                break

        self.output = substep.output

        return self.output

    def render(self) -> str:
        return J2("prompts/steps/tool/tool.j2").render(
            step=self,
            substeps=self._substeps
        )

    def find_substep(self, step_id: str) -> Optional[ToolSubstep]:
        return next((step for step in self._substeps if step.id == step_id), None)

    def add_substep(self, substep: ToolSubstep) -> ToolSubstep:
        substep.attach(self)

        if len(self._substeps) > 0:
            self._substeps[-1].add_child(substep)

        self._substeps.append(substep)

        return substep

    @abstractmethod
    def find_tool(self, tool_name: str) -> Optional[Tool]:
        ...
