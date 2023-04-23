from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.core import BaseTool
from griptape.utils import J2
from griptape.steps import PromptStep
from griptape.artifacts import TextOutput, ErrorOutput

if TYPE_CHECKING:
    from griptape.steps import ToolSubstep


@define
class ToolkitStep(PromptStep, ABC):
    DEFAULT_MAX_SUBSTEPS = 20

    tool_names: list[str] = field(kw_only=True)
    max_substeps: int = field(default=DEFAULT_MAX_SUBSTEPS, kw_only=True)
    _substeps: list[ToolSubstep] = field(factory=list)

    @tool_names.validator
    def validate_tool_names(self, _, tool_names) -> None:
        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tool names have to be unique")

    @property
    def tools(self) -> list[BaseTool]:
        return [
            t for t in [self.structure.tool_loader.load_tool(t) for t in self.tool_names] if t is not None
        ]

    def run(self) -> TextOutput:
        from griptape.steps import ToolSubstep

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

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next(
            (t for t in self.tools if t.name == tool_name),
            None
        )
