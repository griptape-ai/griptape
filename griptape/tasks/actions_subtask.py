from __future__ import annotations
import json
import re
from typing import Optional, TYPE_CHECKING, Callable

import schema
from attr import define, field
from griptape import utils
from griptape.artifacts.actions_artifact import ActionsArtifact
from griptape.utils import remove_null_values_in_dict_recursively
from griptape.mixins import ActionsSubtaskOriginMixin
from griptape.tasks import BaseTextInputTask, BaseTask
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact, ListArtifact
from griptape.events import StartActionsSubtaskEvent, FinishActionsSubtaskEvent

if TYPE_CHECKING:
    from griptape.memory import TaskMemory


@define
class ActionsSubtask(BaseTextInputTask):
    THOUGHT_PATTERN = r"(?s)^Thought:\s*(.*?)$"
    ACTIONS_PATTERN = r"(?s)Actions:[^\[]*(\[.*\])"
    ANSWER_PATTERN = r"(?s)^Answer:\s?([\s\S]*)$"

    parent_task_id: Optional[str] = field(default=None, kw_only=True)
    thought: Optional[str] = field(default=None, kw_only=True)
    actions: list[ActionsArtifact.Action] = field(factory=list, kw_only=True)

    _input: Optional[str | TextArtifact | Callable[[BaseTask], TextArtifact]] = field(default=None)
    _memory: Optional[TaskMemory] = None

    @property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(self._input)

    @input.setter
    def input(self, value: str | TextArtifact | Callable[[BaseTask], TextArtifact]) -> None:
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

    def attach_to(self, parent_task: BaseTask):
        self.parent_task_id = parent_task.id
        self.structure = parent_task.structure
        self.__init_from_input(self.input)

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
            )
        )
        self.structure.logger.info(f"Subtask {self.id}\n{self.input.to_text()}")

    def run(self) -> BaseArtifact:
        try:
            if any(a.name == "error" for a in self.actions):
                errors = [a.input["error"] for a in self.actions if a.name == "error"]

                self.output = ErrorArtifact("\n\n".join(errors))
            else:
                results = self.execute_actions(self.actions)

                self.output = ListArtifact([TextArtifact(name=f"{r[0]} output", value=r[1].to_text()) for r in results])
        except Exception as e:
            self.structure.logger.error(f"Subtask {self.id}\n{e}", exc_info=True)

            self.output = ErrorArtifact(str(e), exception=e)
        finally:
            if self.output is not None:
                return self.output
            else:
                return ErrorArtifact("no tool output")

    def execute_actions(self, actions: list[ActionsArtifact.Action]) -> list[tuple[str, BaseArtifact]]:
        results = utils.execute_futures_dict(
            {a.tag: self.futures_executor.submit(self.execute_action, a) for a in actions}
        )

        return [r for r in results.values()]

    def execute_action(self, action: ActionsArtifact.Action) -> tuple[str, BaseArtifact]:
        if action.tool is not None:
            if action.path is not None:
                output = action.tool.execute(getattr(action.tool, action.path), self, action)
            else:
                output = ErrorArtifact("action path not found")
        else:
            output = ErrorArtifact("action name not found")

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
            )
        )
        self.structure.logger.info(f"Subtask {self.id}\nResponse: {response}")

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
        return json.dumps(self.actions_to_dicts())

    def add_child(self, child: ActionsSubtask) -> ActionsSubtask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        return child

    def add_parent(self, parent: ActionsSubtask) -> ActionsSubtask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        return parent

    def __init_from_input(self, value: TextArtifact) -> None:
        if isinstance(value, ActionsArtifact):
            self.actions = value.actions
        else:
            prompt = value.to_text()
            thought_matches = re.findall(self.THOUGHT_PATTERN, prompt, re.MULTILINE)
            actions_matches = re.findall(self.ACTIONS_PATTERN, prompt, re.DOTALL)
            answer_matches = re.findall(self.ANSWER_PATTERN, prompt, re.MULTILINE)

            if self.thought is None and len(thought_matches) > 0:
                self.thought = thought_matches[-1]

            self.__parse_actions(actions_matches)

            # If there are no actions to take but an answer is provided, set the answer as the output.
            if len(self.actions) == 0 and self.output is None and len(answer_matches) > 0:
                self.output = TextArtifact(answer_matches[-1])

    def __parse_actions(self, actions_matches: list[str]) -> None:
        if len(actions_matches) == 0:
            return

        try:
            data = actions_matches[-1]
            actions_list: list = json.loads(data, strict=False)

            if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
                self.origin_task.actions_schema().validate(actions_list)

            for action_object in actions_list:
                # Load action name; throw exception if the key is not present
                action_tag = action_object["tag"]

                # Load action name; throw exception if the key is not present
                action_name = action_object["name"]

                # Load action method; throw exception if the key is not present
                action_path = action_object["path"]

                # Load optional input value; don't throw exceptions if key is not present
                if "input" in action_object:
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
                    raise Exception(
                        "ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin."
                    )

                new_action = ActionsArtifact.Action(
                    tag=action_tag, name=action_name, path=action_path, input=action_input, tool=tool
                )

                if new_action.tool:
                    if new_action.input:
                        self.__validate_action(new_action)

                # Don't forget to add it to the subtask actions list!
                self.actions.append(new_action)
        except SyntaxError as e:
            self.structure.logger.error(f"Subtask {self.origin_task.id}\nSyntax error: {e}")

            self.actions.append(self.__error_to_action(f"syntax error: {e}"))
        except schema.SchemaError as e:
            self.structure.logger.error(f"Subtask {self.origin_task.id}\nInvalid action JSON: {e}")

            self.actions.append(self.__error_to_action(f"Action JSON validation error: {e}"))
        except Exception as e:
            self.structure.logger.error(f"Subtask {self.origin_task.id}\nError parsing tool action: {e}")

            self.actions.append(self.__error_to_action(f"Action input parsing error: {e}"))

    def __error_to_action(self, error: str) -> ActionsArtifact.Action:
        return ActionsArtifact.Action(tag="error", name="error", input={"error": error})

    def __validate_action(self, action: ActionsArtifact.Action) -> None:
        try:
            if action.path is not None:
                activity = getattr(action.tool, action.path)
            else:
                raise Exception("Action path not found.")

            if activity is not None:
                activity_schema = action.tool.activity_schema(activity)
            else:
                raise Exception("Activity not found.")

            if activity_schema:
                activity_schema.validate(action.input)
        except schema.SchemaError as e:
            self.structure.logger.error(f"Subtask {self.origin_task.id}\nInvalid activity input JSON: {e}")

            self.actions.append(self.__error_to_action(f"Activity input JSON validation error: {e}"))
