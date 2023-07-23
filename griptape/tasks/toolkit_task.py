from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.tasks import ActionSubtask
from griptape import utils
from griptape.core import BaseTool
from griptape.utils import J2
from griptape.tasks import PromptTask
from griptape.artifacts import TextArtifact, ErrorArtifact

if TYPE_CHECKING:
    from griptape.memory.tool import BaseToolMemory
    from griptape.structures import Structure


@define
class ToolkitTask(PromptTask):
    DEFAULT_MAX_STEPS = 20

    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    tool_memory: Optional[BaseToolMemory] = field(default=None, kw_only=True)
    _subtasks: list[ActionSubtask] = field(factory=list)

    def __attrs_post_init__(self) -> None:
        self.set_default_tools_memory(self.tool_memory)

    @tools.validator
    def validate_tools(self, _, tools: list[BaseTool]) -> None:
        tool_names = [t.name for t in tools]

        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tools have to be unique")

    @property
    def memory(self) -> list[BaseToolMemory]:
        unique_memory_dict = {}

        for memories in [tool.output_memory for tool in self.tools if tool.output_memory]:
            for memory_list in memories.values():
                for memory in memory_list:
                    if memory.id not in unique_memory_dict:
                        unique_memory_dict[memory.id] = memory

        return list(unique_memory_dict.values())

    def set_default_tools_memory(self, memory: BaseToolMemory) -> None:
        self.tool_memory = memory

        for tool in self.tools:
            if self.tool_memory:
                if tool.input_memory is None:
                    tool.input_memory = [self.tool_memory]
                if tool.output_memory is None:
                    tool.output_memory = {
                        a.name: [self.tool_memory]
                        for a in tool.activities() if tool.activity_uses_default_memory(a)
                    }

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
        subtask.attach_to(self)

        if len(self._subtasks) > 0:
            self._subtasks[-1].add_child(subtask)

        self._subtasks.append(subtask)

        return subtask

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next(
            (t for t in self.tools if t.name == tool_name),
            None
        )

    def find_memory(self, memory_id: str) -> Optional[BaseToolMemory]:
        return next(
            (r for r in self.memory if r.id == memory_id),
            None
        )

    def prompt_stack(self, structure: Structure) -> list[str]:
        from griptape.tasks import ToolkitTask

        tools = self.tools if isinstance(self, ToolkitTask) else []
        memories = [r for r in self.memory if len(r.activities()) > 0] if isinstance(self, ToolkitTask) else []
        action_schema = utils.minify_json(
            json.dumps(
                ActionSubtask.ACTION_SCHEMA.json_schema("ActionSchema")
            )
        )

        stack = [
            J2("prompts/tasks/toolkit/base.j2").render(
                rulesets=structure.rulesets,
                action_schema=action_schema,
                tool_names=str.join(", ", [tool.name for tool in tools]),
                tools=[J2("prompts/tool.j2").render(tool=tool) for tool in tools],
                memory_ids=str.join(", ", [memory.id for memory in memories]),
                memories=[J2("prompts/memory/tool.j2").render(memory=memory) for memory in memories]
            )
        ]

        return stack
