from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Callable, Optional

import schema
from attrs import define, field

from griptape import utils
from griptape.artifacts import ActionArtifact, BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.common import ToolAction
from griptape.events import FinishActionsSubtaskEvent, StartActionsSubtaskEvent
from griptape.mixins import ActionsSubtaskOriginMixin
from griptape.tasks import BaseTask
from griptape.utils import remove_null_values_in_dict_recursively

if TYPE_CHECKING:
    from griptape.memory import TaskMemory


@define
class ActionsSubtask(BaseTask):
    THOUGHT_PATTERN = r"(?s)^Thought:\s*(.*?)$"
    ACTIONS_PATTERN = r"(?s)Actions:[^\[]*(\[.*\])"
    ANSWER_PATTERN = r"(?s)^Answer:\s?([\s\S]*)$"

    parent_task_id: Optional[str] = field(default=None, kw_only=True)
    thought: Optional[str] = field(default=None, kw_only=True)
    actions: list[ToolAction] = field(factory=list, kw_only=True)
    output: Optional[BaseArtifact] = field(default=None, init=False)
    _input: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
        alias="input",
    )
    _memory: Optional[TaskMemory] = None

    @property
    def input(self) -> TextArtifact | ListArtifact:
        return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    @property
    def origin_task(self) -> BaseTask:
        if self.parent_task_id:
            return self.structure.find_task(self.parent_task_id)
        else:
            raise Exception("ActionSubtask has no parent task.")

    @property
    def parents(self) -> list[BaseTask]:
        if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
            return [self.origin_task.find_subtask(parent_id) for parent_id in self.parent_ids]
        else:
            raise Exception("ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin.")

    @property
    def children(self) -> list[BaseTask]:
        if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
            return [self.origin_task.find_subtask(child_id) for child_id in self.child_ids]
        else:
            raise Exception("ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin.")

    def attach_to(self, parent_task: BaseTask) -> None:
        self.parent_task_id = parent_task.id
        self.structure = parent_task.structure

        try:
            if isinstance(self.input, TextArtifact):
                self.__init_from_prompt(self.input.to_text())
            else:
                self.__init_from_artifacts(self.input)
        except Exception as e:
            self.structure.logger.error("Subtask %s\nError parsing tool action: %s", self.origin_task.id, e)

            self.output = ErrorArtifact(f"ToolAction input parsing error: {e}", exception=e)

    def before_run(self) -> None:
        self.structure.publish_event(
            StartActionsSubtaskEvent(
                task_id=self.id,
                task_parent_ids=self.parent_ids,
                task_child_ids=self.child_ids,
                task_input=self.input,
                task_output=self.output,
                subtask_parent_task_id=self.parent_task_id,
                subtask_thought=self.thought,
                subtask_actions=self.actions_to_dicts(),
            ),
        )

        parts = [
            f"Subtask {self.id}",
            *([f"\nThought: {self.thought}"] if self.thought is not None else []),
            f"\nActions: {self.actions_to_json()}",
        ]
        self.structure.logger.info("".join(parts))

    def run(self) -> BaseArtifact:
        try:
            if any(isinstance(a.output, ErrorArtifact) for a in self.actions):
                errors = [a.output.value for a in self.actions if isinstance(a.output, ErrorArtifact)]

                self.output = ErrorArtifact("\n\n".join(errors))
            else:
                results = self.execute_actions(self.actions)

                actions_output = []
                for result in results:
                    tag, output = result
                    output.name = f"{tag} output"

                    actions_output.append(output)
                self.output = ListArtifact(actions_output)
        except Exception as e:
            self.structure.logger.exception("Subtask %s\n%s", self.id, e)

            self.output = ErrorArtifact(str(e), exception=e)
        if self.output is not None:
            return self.output
        else:
            return ErrorArtifact("no tool output")

    def execute_actions(self, actions: list[ToolAction]) -> list[tuple[str, BaseArtifact]]:
        with self.futures_executor_fn() as executor:
            results = utils.execute_futures_dict({a.tag: executor.submit(self.execute_action, a) for a in actions})

        return list(results.values())

    def execute_action(self, action: ToolAction) -> tuple[str, BaseArtifact]:
        if action.tool is not None:
            if action.path is not None:
                output = action.tool.execute(getattr(action.tool, action.path), self, action)
            else:
                output = ErrorArtifact("action path not found")
        else:
            output = ErrorArtifact("action name not found")
        action.output = output

        return action.tag, output

    def after_run(self) -> None:
        response = self.output.to_text() if isinstance(self.output, BaseArtifact) else str(self.output)

        self.structure.publish_event(
            FinishActionsSubtaskEvent(
                task_id=self.id,
                task_parent_ids=self.parent_ids,
                task_child_ids=self.child_ids,
                task_input=self.input,
                task_output=self.output,
                subtask_parent_task_id=self.parent_task_id,
                subtask_thought=self.thought,
                subtask_actions=self.actions_to_dicts(),
            ),
        )
        self.structure.logger.info("Subtask %s\nResponse: %s", self.id, response)

    def actions_to_dicts(self) -> list[dict]:
        json_list = []

        for action in self.actions:
            json_dict = {}

            if action.tag:
                json_dict["tag"] = action.tag

            if action.name:
                json_dict["name"] = action.name

            if action.path:
                json_dict["path"] = action.path

            if action.input:
                json_dict["input"] = action.input

            json_list.append(json_dict)

        return json_list

    def actions_to_json(self) -> str:
        return json.dumps(self.actions_to_dicts(), indent=2)

    def _process_task_input(
        self,
        task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact],
    ) -> TextArtifact | ListArtifact:
        if isinstance(task_input, (TextArtifact, ListArtifact)):
            return task_input
        elif isinstance(task_input, ActionArtifact):
            return ListArtifact([task_input])
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, str):
            return self._process_task_input(TextArtifact(task_input))
        elif isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            raise ValueError(f"Invalid input type: {type(task_input)} ")

    def __init_from_prompt(self, value: str) -> None:
        thought_matches = re.findall(self.THOUGHT_PATTERN, value, re.MULTILINE)
        actions_matches = re.findall(self.ACTIONS_PATTERN, value, re.DOTALL)
        answer_matches = re.findall(self.ANSWER_PATTERN, value, re.MULTILINE)

        if self.thought is None and thought_matches:
            self.thought = thought_matches[-1]

        self.__parse_actions(actions_matches)

        # If there are no actions to take but an answer is provided, set the answer as the output.
        if len(self.actions) == 0 and self.output is None and answer_matches:
            self.output = TextArtifact(answer_matches[-1])

    def __init_from_artifacts(self, artifacts: ListArtifact) -> None:
        """Parses the input Artifacts to extract the thought and actions.

        Text Artifacts are used to extract the thought, and ToolAction Artifacts are used to extract the actions.

        Args:
            artifacts: The input Artifacts.

        Returns:
            None
        """
        self.actions = [
            self.__process_action_object(artifact.value.to_dict())
            for artifact in artifacts.value
            if isinstance(artifact, ActionArtifact)
        ]

        thoughts = [artifact.value for artifact in artifacts.value if isinstance(artifact, TextArtifact)]
        if thoughts:
            self.thought = thoughts[0]

    def __parse_actions(self, actions_matches: list[str]) -> None:
        if len(actions_matches) == 0:
            return
        try:
            data = actions_matches[-1]
            actions_list: list[dict] = json.loads(data, strict=False)

            self.actions = [self.__process_action_object(action_object) for action_object in actions_list]
        except json.JSONDecodeError as e:
            self.structure.logger.exception("Subtask %s\nInvalid actions JSON: %s", self.origin_task.id, e)

            self.output = ErrorArtifact(f"Actions JSON decoding error: {e}", exception=e)

    def __process_action_object(self, action_object: dict) -> ToolAction:
        # Load action tag; throw exception if the key is not present
        action_tag = action_object["tag"]

        # Load action name; throw exception if the key is not present
        action_name = action_object["name"]

        # Load action method; throw exception if the key is not present
        action_path = action_object["path"]

        # Load optional input value; don't throw exceptions if key is not present
        if "input" in action_object:
            # Some LLMs don't support nested parameters and therefore won't generate "values".
            # So we need to manually add it here.
            if "values" not in action_object["input"]:
                action_object["input"] = {"values": action_object["input"]}

            # The schema library has a bug, where something like `Or(str, None)` doesn't get
            # correctly translated into JSON schema. For some optional input fields LLMs sometimes
            # still provide null value, which trips up the validator. The temporary solution that
            # works is to strip all key-values where value is null.
            action_input = remove_null_values_in_dict_recursively(action_object["input"])
        else:
            action_input = {}

        # Load the action itself
        if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
            tool = self.origin_task.find_tool(action_name)
        else:
            raise Exception("ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin.")

        action = ToolAction(tag=action_tag, name=action_name, path=action_path, input=action_input, tool=tool)

        if action.tool and action.input:
            self.__validate_action(action)

        return action

    def __validate_action(self, action: ToolAction) -> None:
        try:
            if action.path is not None:
                activity = getattr(action.tool, action.path)
            else:
                raise Exception("ToolAction path not found.")

            if activity is not None:
                activity_schema = action.tool.activity_schema(activity)
            else:
                raise Exception("Activity not found.")

            if activity_schema:
                activity_schema.validate(action.input)
        except schema.SchemaError as e:
            self.structure.logger.exception("Subtask %s\nInvalid action JSON: %s", self.origin_task.id, e)

            action.output = ErrorArtifact(f"Activity input JSON validation error: {e}", exception=e)
        except SyntaxError as e:
            self.structure.logger.exception("Subtask %s\nSyntax error: %s", self.origin_task.id, e)

            action.output = ErrorArtifact(f"Syntax error: {e}", exception=e)
