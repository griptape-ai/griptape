from __future__ import annotations
import ast
import json
import re
from typing import TYPE_CHECKING, Optional
from attr import define, field
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from griptape.artifacts import TextOutput, ErrorOutput
from griptape.tasks import PromptTask
from griptape.core import BaseTool
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.tasks import ToolkitTask


@define
class ToolSubtask(PromptTask):
    THOUGHT_PATTERN = r"^Thought:\s*(.*)$"
    ACTION_PATTERN = r"^Action:\s*({.*})$"
    OUTPUT_PATTERN = r"^Output:\s?([\s\S]*)$"
    INVALID_ACTION_ERROR_MSG = f"invalid action input, try again"

    parent_task_id: Optional[str] = field(default=None, kw_only=True)
    thought: Optional[str] = field(default=None, kw_only=True)
    tool_name: Optional[str] = field(default=None, kw_only=True)
    tool_action: Optional[str] = field(default=None, kw_only=True)
    tool_value: Optional[str] = field(default=None, kw_only=True)

    _tool: Optional[BaseTool] = None

    def attach(self, parent_task: ToolkitTask):
        self.parent_task_id = parent_task.id
        self.structure = parent_task.structure
        self.__init_from_prompt(self.input.value)

    @property
    def task(self) -> Optional[ToolkitTask]:
        return self.structure.find_task(self.parent_task_id)

    @property
    def parents(self) -> list[ToolSubtask]:
        return [self.task.find_subtask(parent_id) for parent_id in self.parent_ids]

    @property
    def children(self) -> list[ToolSubtask]:
        return [self.task.find_subtask(child_id) for child_id in self.child_ids]

    def before_run(self) -> None:
        self.structure.logger.info(f"Subtask {self.id}\n{self.input.value}")

    def run(self) -> BaseArtifact:
        try:
            if self.tool_name == "error":
                self.output = ErrorOutput(self.tool_value, task=self.task)
            else:
                if self._tool:
                    observation = self.structure.tool_loader.executor.execute(
                        getattr(self._tool, self.tool_action),
                        self.tool_value.encode()
                    ).decode()
                else:
                    observation = "tool not found"

                self.output = TextOutput(observation)
        except Exception as e:
            self.structure.logger.error(f"Subtask {self.id}\n{e}", exc_info=True)

            self.output = ErrorOutput(str(e), exception=e, task=self.task)
        finally:
            return self.output

    def after_run(self) -> None:
        self.structure.logger.info(f"Subtask {self.id}\nObservation: {self.output.value}")

    def render(self) -> str:
        return J2("prompts/tasks/tool/subtask.j2").render(
            subtask=self
        )

    def to_json(self) -> str:
        json_dict = {}

        if self.tool_name:
            json_dict["tool"] = self.tool_name

        if self.tool_action:
            json_dict["action"] = self.tool_action

        if self.tool_value:
            json_dict["value"] = self.tool_value

        return json.dumps(json_dict)

    def add_child(self, child: ToolSubtask) -> ToolSubtask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        return child

    def add_parent(self, parent: ToolSubtask) -> ToolSubtask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        return parent

    def __init_from_prompt(self, value: str) -> None:
        thought_matches = re.findall(self.THOUGHT_PATTERN, value, re.MULTILINE)
        action_matches = re.findall(self.ACTION_PATTERN, value, re.MULTILINE)
        output_matches = re.findall(self.OUTPUT_PATTERN, value, re.MULTILINE)

        if self.thought is None and len(thought_matches) > 0:
            self.thought = thought_matches[-1]

        if len(action_matches) > 0:
            try:
                parsed_value = ast.literal_eval(action_matches[-1])

                # Load the tool name; throw exception if the key is not present
                if self.tool_name is None:
                    self.tool_name = parsed_value["tool"]

                # Load the tool action; throw exception if the key is not present
                if self.tool_action is None:
                    self.tool_action = parsed_value["action"]

                # Load the tool itself
                if self.tool_name:
                    self._tool = self.task.find_tool(self.tool_name)

                # Validate input based on tool schema
                if self._tool:
                    validate(
                        instance=parsed_value["value"],
                        schema=self._tool.action_schema(getattr(self._tool, self.tool_action))
                    )

                # Load optional input value; don't throw exceptions if key is not present
                if self.tool_value is None:
                    self.tool_value = str(parsed_value.get("value"))

            except SyntaxError as e:
                self.structure.logger.error(f"Subtask {self.task.id}\nSyntax error: {e}")

                self.tool_name = "error"
                self.tool_value = f"syntax error: {e}"
            except ValidationError as e:
                self.structure.logger.error(f"Subtask {self.task.id}\nInvalid JSON: {e}")

                self.tool_name = "error"
                self.tool_value = f"JSON validation error: {e}"
            except Exception as e:
                self.structure.logger.error(f"Subtask {self.task.id}\nError parsing tool action: {e}")

                self.tool_name = "error"
                self.tool_value = f"error: {self.INVALID_ACTION_ERROR_MSG}"
        elif self.output is None and len(output_matches) > 0:
            self.output = TextOutput(output_matches[-1])
