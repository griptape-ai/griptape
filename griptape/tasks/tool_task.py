import json
from typing import Optional
import schema
from attr import define, field
from schema import Schema, Literal
from griptape import utils
from griptape.artifacts import TextArtifact, InfoArtifact
from griptape.memory.tool import BaseToolMemory
from griptape.tasks import PromptTask, ActionSubtask
from griptape.tools import BaseTool
from griptape.utils import J2, ActionSubtaskOriginMixin


@define
class ToolTask(PromptTask, ActionSubtaskOriginMixin):
    TOOL_SCHEMA = Schema(
        schema={
            Literal(
                "type",
                description="Action type"
            ): schema.Or("tool"),
            Literal(
                "name",
                description="Tool name"
            ): str,
            Literal(
                "activity",
                description="Tool activity"
            ): str,
            schema.Optional(
                Literal(
                    "input",
                    description="Optional tool activity input object"
                )
            ): dict
        }
    )

    tool: BaseTool = field(kw_only=True)
    subtask: Optional[ActionSubtask] = field(default=None, kw_only=True)

    def default_system_template_generator(self, _: PromptTask) -> str:
        tool_schema = utils.minify_json(
            json.dumps(
                self.TOOL_SCHEMA.json_schema("ToolSchema")
            )
        )

        return J2("tasks/tool_task/system.j2").render(
            rulesets=self.structure.rulesets,
            tool_schema=tool_schema,
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
