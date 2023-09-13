import json
from typing import Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import TextArtifact, InfoArtifact
from griptape.memory.tool import BaseToolMemory
from griptape.tasks import PromptTask, ActionSubtask
from griptape.tools import BaseTool
from griptape.utils import J2
from griptape.mixins import ActionSubtaskOriginMixin


@define
class ToolTask(PromptTask, ActionSubtaskOriginMixin):
    tool: BaseTool = field(kw_only=True)
    subtask: Optional[ActionSubtask] = field(default=None, kw_only=True)

    @property
    def action_types(self) -> list[str]:
        return ["tool"]

    def default_system_template_generator(self, _: PromptTask) -> str:
        action_schema = utils.minify_json(
            json.dumps(
                ActionSubtask.action_schema(self.action_types).json_schema("ToolSchema")
            )
        )

        return J2("tasks/tool_task/system.j2").render(
            rulesets=self.all_rulesets,
            action_schema=action_schema,
            tool=J2("tasks/partials/_tool.j2").render(tool=self.tool)
        )

    def run(self) -> TextArtifact:
        output = self.active_driver().run(prompt_stack=self.prompt_stack).to_text()

        subtask = self.add_subtask(
            ActionSubtask(
                f"Action: {output}"
            )
        )

        subtask.before_run()
        subtask.run()
        subtask.after_run()

        if subtask.output:
            self.output = subtask.output
        else:
            self.output = InfoArtifact("No tool output")

        return self.output

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        if self.tool.name == tool_name:
            return self.tool
        else:
            return None

    def find_memory(self, memory_name: str) -> Optional[BaseToolMemory]:
        return None

    def find_subtask(self, subtask_id: str) -> Optional[ActionSubtask]:
        return self.subtask if self.subtask.id == subtask_id else None

    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        self.subtask = subtask
        self.subtask.attach_to(self)

        return self.subtask
