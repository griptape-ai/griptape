from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.core import BaseTool
from griptape.utils import J2
from griptape.tasks import PromptTask
from griptape.artifacts import TextArtifact, ErrorArtifact

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask
    from griptape.ramps import BaseRamp


@define
class ToolkitTask(PromptTask, ABC):
    DEFAULT_MAX_STEPS = 20

    tool_names: list[str] = field(kw_only=True)
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    _subtasks: list[ActionSubtask] = field(factory=list)

    @tool_names.validator
    def validate_tool_names(self, _, tool_names: list[str]) -> None:
        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tool names have to be unique")

    @property
    def tools(self) -> list[BaseTool]:
        return [
            t for t in [self.structure.tool_loader.load_tool(t) for t in self.tool_names] if t is not None
        ]

    @property
    def ramps(self) -> list[BaseRamp]:
        unique_ramps_dict = {}

        for ramps_dict in [tool.ramps for tool in self.tools]:
            for ramps_list in ramps_dict.values():
                for ramps in ramps_list:
                    if ramps.name not in unique_ramps_dict:
                        unique_ramps_dict[ramps.name] = ramps

        return list(unique_ramps_dict.values())

    def run(self) -> TextArtifact:
        from griptape.tasks import ActionSubtask

        self._subtasks.clear()

        subtask = self.add_subtask(
            ActionSubtask(
                self.active_driver().run(value=self.structure.to_prompt_string(self)).value
            )
        )

        while True:
            if subtask.output is None:
                if len(self._subtasks) >= self.max_subtasks:
                    subtask.output = ErrorArtifact(
                        f"Exceeded tool limit of {self.max_subtasks} subtasks per task",
                        task=self
                    )
                elif subtask.action_name is None:
                    # handle case when the LLM failed to follow the ReAct prompt and didn't return a proper action
                    subtask.output = TextArtifact(subtask.prompt_template)
                else:
                    subtask.before_run()
                    subtask.run()
                    subtask.after_run()

                    subtask = self.add_subtask(
                        ActionSubtask(
                            self.active_driver().run(value=self.structure.to_prompt_string(self)).value
                        )
                    )
            else:
                break

        self.output = subtask.output

        return self.output

    def render(self) -> str:
        return J2("prompts/tasks/tool/tool.j2").render(
            subtask=self,
            subtasks=self._subtasks
        )

    def find_subtask(self, task_id: str) -> Optional[ActionSubtask]:
        return next((subtask for subtask in self._subtasks if subtask.id == task_id), None)

    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        subtask.attach(self)

        if len(self._subtasks) > 0:
            self._subtasks[-1].add_child(subtask)

        self._subtasks.append(subtask)

        return subtask

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next(
            (t for t in self.tools if t.name == tool_name),
            None
        )

    def find_ramps(self, ramp_name: str) -> Optional[BaseRamp]:
        return next(
            (r for r in self.ramps if r.name == ramp_name),
            None
        )
