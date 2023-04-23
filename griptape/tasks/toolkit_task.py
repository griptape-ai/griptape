from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.core import BaseTool
from griptape.utils import J2
from griptape.tasks import PromptTask
from griptape.artifacts import TextOutput, ErrorOutput

if TYPE_CHECKING:
    from griptape.tasks import ToolStep


@define
class ToolkitTask(PromptTask, ABC):
    DEFAULT_MAX_STEPS = 20

    tool_names: list[str] = field(kw_only=True)
    max_steps: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    _steps: list[ToolStep] = field(factory=list)

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
        from griptape.tasks import ToolStep

        self._steps.clear()

        step = self.add_step(
            ToolStep(
                self.active_driver().run(value=self.structure.to_prompt_string(self)).value
            )
        )

        while True:
            if step.output is None:
                if len(self._steps) >= self.max_steps:
                    step.output = ErrorOutput(
                        f"Exceeded tool limit of {self.max_steps} steps per task",
                        task=self
                    )
                elif step.tool_name is None:
                    # handle case when the LLM failed to follow the ReAct prompt and didn't return a proper action
                    step.output = TextOutput(step.prompt_template)
                else:
                    step.before_run()
                    step.run()
                    step.after_run()

                    step = self.add_step(
                        ToolStep(
                            self.active_driver().run(value=self.structure.to_prompt_string(self)).value
                        )
                    )
            else:
                break

        self.output = step.output

        return self.output

    def render(self) -> str:
        return J2("prompts/tasks/tool/tool.j2").render(
            step=self,
            steps=self._steps
        )

    def find_step(self, task_id: str) -> Optional[ToolStep]:
        return next((step for step in self._steps if step.id == task_id), None)

    def add_step(self, step: ToolStep) -> ToolStep:
        step.attach(self)

        if len(self._steps) > 0:
            self._steps[-1].add_child(step)

        self._steps.append(step)

        return step

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next(
            (t for t in self.tools if t.name == tool_name),
            None
        )
