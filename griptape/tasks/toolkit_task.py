from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.tasks import ActionSubtask
from griptape import utils
from griptape.core import BaseTool
from griptape.executors import BaseExecutor, LocalExecutor
from griptape.utils import J2
from griptape.tasks import PromptTask
from griptape.artifacts import TextArtifact, ErrorArtifact

if TYPE_CHECKING:
    from griptape.ramps import BaseRamp
    from griptape.structures import Structure


@define
class ToolkitTask(PromptTask):
    DEFAULT_MAX_STEPS = 20

    tools: list[BaseTool] = field(factory=list, kw_only=True)
    executor: BaseExecutor = field(default=LocalExecutor(), kw_only=True)
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    _subtasks: list[ActionSubtask] = field(factory=list)

    @tools.validator
    def validate_tools(self, _, tools: list[BaseTool]) -> None:
        tool_names = [t.name for t in tools]

        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tools have to be unique")

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
                self.active_driver().run(value=self.structure.to_prompt_string(self)).to_text()
            )
        )

        while True:
            if subtask.output is None:
                if len(self._subtasks) >= self.max_subtasks:
                    subtask.output = ErrorArtifact(
                        f"Exceeded tool limit of {self.max_subtasks} subtasks per task"
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
                            self.active_driver().run(value=self.structure.to_prompt_string(self)).to_text()
                        )
                    )
            else:
                break

        self.output = subtask.output

        return self.output

    def render(self) -> str:
        return J2("prompts/tasks/toolkit/conversation.j2").render(
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

    def find_ramp(self, ramp_name: str) -> Optional[BaseRamp]:
        return next(
            (r for r in self.ramps if r.name == ramp_name),
            None
        )

    def prompt_stack(self, structure: Structure) -> list[str]:
        from griptape.tasks import ToolkitTask

        tools = self.tools if isinstance(self, ToolkitTask) else []
        ramps = [r for r in self.ramps if len(r.activities()) > 0] if isinstance(self, ToolkitTask) else []
        action_schema = utils.minify_json(
            json.dumps(
                ActionSubtask.ACTION_SCHEMA.json_schema("ActionSchema")
            )
        )

        stack = [
            J2("prompts/tasks/toolkit/base.j2").render(
                rulesets=structure.rulesets,
                action_schema=action_schema,
                ramp_names=str.join(", ", [ramp.name for ramp in ramps]),
                ramps=[J2("prompts/ramp.j2").render(ramp=ramp) for ramp in ramps],
                tool_names=str.join(", ", [tool.name for tool in tools]),
                tools=[J2("prompts/tool.j2").render(tool=tool) for tool in tools]
            )
        ]

        return stack
