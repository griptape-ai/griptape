from __future__ import annotations
import json
import re
from typing import Optional, TYPE_CHECKING
import schema
from attr import define, field
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.utils import remove_null_values_in_dict_recursively
from griptape.mixins import ActivityMixin, ActionSubtaskOriginMixin
from griptape.tasks import PromptTask, BaseTask
from griptape.artifacts import BaseArtifact
from griptape.events import StartActionSubtaskEvent, FinishActionSubtaskEvent

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tools import BaseTool


@define
class ActionSubtask(PromptTask):
    THOUGHT_PATTERN = r"(?s)^Thought:\s*(.*?)$"
    ACTION_PATTERN = r"(?s)Action:[^{]*({.*})"
    ANSWER_PATTERN = r"(?s)^Answer:\s?([\s\S]*)$"
    ACTION_SCHEMA = Schema(
        description="Actions have name, path, and input object.",
        schema={
            Literal("name", description="Action name"): str,
            Literal("path", description="Action path"): str,
            schema.Optional(Literal("input", description="Optional action path input values object")): {"values": dict},
        },
    )

    parent_task_id: str | None = field(default=None, kw_only=True)
    thought: str | None = field(default=None, kw_only=True)
    action_name: str | None = field(default=None, kw_only=True)
    action_path: str | None = field(default=None, kw_only=True)
    action_input: dict | None = field(default=None, kw_only=True)

    _tool: BaseTool | None = None
    _memory: TaskMemory | None = None

    @property
    def input(self) -> TextArtifact:
        return TextArtifact(self.input_template)

    @property
    def origin_task(self) -> ActionSubtaskOriginMixin | None:
        return self.structure.find_task(self.parent_task_id)

    @property
    def parents(self) -> list[ActionSubtask]:
        return [self.origin_task.find_subtask(parent_id) for parent_id in self.parent_ids]

    @property
    def children(self) -> list[ActionSubtask]:
        return [self.origin_task.find_subtask(child_id) for child_id in self.child_ids]

    def attach_to(self, parent_task: BaseTask):
        self.parent_task_id = parent_task.id
        self.structure = parent_task.structure
        self.__init_from_prompt(self.input.to_text())

    def before_run(self) -> None:
        self.structure.publish_event(StartActionSubtaskEvent.from_task(self))
        self.structure.logger.info(f"Subtask {self.id}\n{self.input.to_text()}")

    def run(self) -> BaseArtifact:
        try:
            if self.action_name == "error":
                self.output = ErrorArtifact(str(self.action_input))
            else:
                if self._tool:
                    response = self._tool.execute(getattr(self._tool, self.action_path), self)
                else:
                    response = ErrorArtifact("tool not found")

                self.output = response
        except Exception as e:
            self.structure.logger.error(f"Subtask {self.id}\n{e}", exc_info=True)

            self.output = ErrorArtifact(str(e))
        finally:
            return self.output

    def after_run(self) -> None:
        response = self.output.to_text() if isinstance(self.output, BaseArtifact) else str(self.output)

        self.structure.publish_event(FinishActionSubtaskEvent.from_task(self))
        self.structure.logger.info(f"Subtask {self.id}\nResponse: {response}")

    def action_to_json(self) -> str:
        json_dict = {}

        if self.action_name:
            json_dict["name"] = self.action_name

        if self.action_path:
            json_dict["path"] = self.action_path

        if self.action_input:
            json_dict["input"] = self.action_input

        return json.dumps(json_dict)

    def add_child(self, child: ActionSubtask) -> ActionSubtask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        return child

    def add_parent(self, parent: ActionSubtask) -> ActionSubtask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        return parent

    def __init_from_prompt(self, value: str) -> None:
        thought_matches = re.findall(self.THOUGHT_PATTERN, value, re.MULTILINE)
        action_matches = re.findall(self.ACTION_PATTERN, value, re.DOTALL)
        answer_matches = re.findall(self.ANSWER_PATTERN, value, re.MULTILINE)

        if self.thought is None and len(thought_matches) > 0:
            self.thought = thought_matches[-1]

        if len(action_matches) > 0:
            try:
                data = action_matches[-1]
                action_object: dict = json.loads(data, strict=False)

                validate(instance=action_object, schema=self.ACTION_SCHEMA.schema)

                # Load action name; throw exception if the key is not present
                if self.action_name is None:
                    self.action_name = action_object["name"]

                # Load action method; throw exception if the key is not present
                if self.action_path is None:
                    self.action_path = action_object["path"]

                # Load optional input value; don't throw exceptions if key is not present
                if self.action_input is None and "input" in action_object:
                    # The schema library has a bug, where something like `Or(str, None)` doesn't get
                    # correctly translated into JSON schema. For some optional input fields LLMs sometimes
                    # still provide null value, which trips up the validator. The temporary solution that
                    # works is to strip all key-values where value is null.
                    self.action_input = remove_null_values_in_dict_recursively(action_object["input"])

                # Load the action itself
                if self.action_name:
                    self._tool = self.origin_task.find_tool(self.action_name)

                if self._tool:
                    self.__validate_action_input(self.action_input, self._tool)
            except SyntaxError as e:
                self.structure.logger.error(f"Subtask {self.origin_task.id}\nSyntax error: {e}")

                self.action_name = "error"
                self.action_input = {"error": f"syntax error: {e}"}
            except ValidationError as e:
                self.structure.logger.error(f"Subtask {self.origin_task.id}\nInvalid action JSON: {e}")

                self.action_name = "error"
                self.action_input = {"error": f"Action JSON validation error: {e}"}
            except Exception as e:
                self.structure.logger.error(f"Subtask {self.origin_task.id}\nError parsing tool action: {e}")

                self.action_name = "error"
                self.action_input = {"error": f"Action input parsing error: {e}"}
        elif self.output is None and len(answer_matches) > 0:
            self.output = TextArtifact(answer_matches[-1])

    def __validate_action_input(self, action_input: dict, mixin: ActivityMixin) -> None:
        try:
            activity_schema = mixin.activity_schema(getattr(mixin, self.action_path))

            if activity_schema:
                validate(instance=action_input, schema=activity_schema)
        except ValidationError as e:
            self.structure.logger.error(f"Subtask {self.origin_task.id}\nInvalid activity input JSON: {e}")

            self.action_name = "error"
            self.action_input = {"error": f"Activity input JSON validation error: {e}"}
