from __future__ import annotations
import json
from typing import Optional, TYPE_CHECKING
from attr import define, field
from griptape import utils
from griptape.artifacts import TextArtifact, InfoArtifact
from griptape.tasks import PromptTask, ActionSubtask
from griptape.tools import BaseTool
from griptape.utils import J2
from griptape.mixins import ActionSubtaskOriginMixin

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.structures import Structure


@define
class ToolTask(PromptTask, ActionSubtaskOriginMixin):
    tool: BaseTool = field(kw_only=True)
    subtask: ActionSubtask | None = field(default=None, kw_only=True)
    task_memory: TaskMemory | None = field(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        self.set_default_tools_memory(self.task_memory)

    def preprocess(self, structure: Structure) -> ToolTask:
        super().preprocess(structure)

        if self.task_memory is None:
            self.set_default_tools_memory(structure.task_memory)

        return self

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/tool_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets),
            action_schema=utils.minify_json(json.dumps(self.tool.schema())),
            meta_memory=J2("memory/meta/meta_memory.j2").render(meta_memories=self.meta_memories),
        )

    def run(self) -> TextArtifact:
        prompt_output = self.active_driver().run(prompt_stack=self.prompt_stack).to_text()

        subtask = self.add_subtask(ActionSubtask(f"Action: {prompt_output}"))

        subtask.before_run()
        subtask.run()
        subtask.after_run()

        if subtask.output:
            self.output = subtask.output
        else:
            self.output = InfoArtifact("No tool output")

        return self.output

    def find_tool(self, tool_name: str) -> BaseTool | None:
        if self.tool.name == tool_name:
            return self.tool
        else:
            return None

    def find_memory(self, memory_name: str) -> TaskMemory | None:
        return None

    def find_subtask(self, subtask_id: str) -> ActionSubtask | None:
        return self.subtask if self.subtask.id == subtask_id else None

    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        self.subtask = subtask
        self.subtask.attach_to(self)

        return self.subtask

    def set_default_tools_memory(self, memory: TaskMemory) -> None:
        self.task_memory = memory

        if self.task_memory:
            if self.tool.input_memory is None:
                self.tool.input_memory = [self.task_memory]
            if self.tool.output_memory is None and self.tool.off_prompt:
                self.tool.output_memory = {a.name: [self.task_memory] for a in self.tool.activities()}
