from __future__ import annotations
import json
from typing import Optional, TYPE_CHECKING
from attr import define, field
from griptape import utils
from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.tasks import PromptTask, ActionSubtask
from griptape.tools import BaseTool
from griptape.utils import J2
from griptape.mixins import ActionSubtaskOriginMixin

if TYPE_CHECKING:
    from griptape.memory import TaskMemory


@define
class ToolTask(PromptTask, ActionSubtaskOriginMixin):
    tool: BaseTool = field(kw_only=True)
    subtask: Optional[ActionSubtask] = field(default=None, kw_only=True)
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/tool_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets),
            action_schema=utils.minify_json(json.dumps(self.tool.schema())),
            meta_memory=J2("memory/meta/meta_memory.j2").render(meta_memories=self.meta_memories),
        )

    def run(self) -> BaseArtifact:
        prompt_output = self.active_driver().run(prompt_stack=self.prompt_stack).to_text()

        subtask = self.add_subtask(ActionSubtask(f"Action: {prompt_output}"))

        subtask.before_run()
        output = subtask.run()
        subtask.after_run(output)

        if subtask.output:
            return subtask.output
        else:
            return InfoArtifact("No tool output")

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        if self.tool.name == tool_name:
            return self.tool
        else:
            return None

    def find_memory(self, memory_name: str) -> Optional[TaskMemory]:
        return None

    def find_subtask(self, subtask_id: str) -> Optional[ActionSubtask]:
        return self.subtask if self.subtask.id == subtask_id else None

    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        self.subtask = subtask
        self.subtask.attach_to(self)

        return self.subtask

    def set_default_task_memory(self, memory: TaskMemory) -> None:
        super().set_default_task_memory(memory)

        if self.task_memory:
            if self.tool.input_memory is None:
                self.tool.input_memory = [self.task_memory]
            if self.tool.output_memory is None and self.tool.off_prompt:
                self.tool.output_memory = {a.name: [self.task_memory] for a in self.tool.activities()}
