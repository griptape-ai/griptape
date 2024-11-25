from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Callable, Optional, Union

import schema
from attrs import Factory, define, field

from griptape import utils
from griptape.artifacts import ActionArtifact, BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack, ToolAction
from griptape.configs import Defaults
from griptape.events import EventBus, FinishActionsSubtaskEvent, StartActionsSubtaskEvent
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks.base_subtask import BaseSubtask
from griptape.utils import J2, remove_null_values_in_dict_recursively, with_contextvars

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.memory import TaskMemory
    from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class ActionsSubtask(BaseSubtask):
    # Stop sequence for chain-of-thought in the framework. Using this "token-like" string to make it more unique,
    # so that it doesn't trigger on accident.
    RESPONSE_STOP_SEQUENCE = "<|Response|>"
    THOUGHT_PATTERN = r"(?s)^Thought:\s*(.*?)$"
    ACTIONS_PATTERN = r"(?s)Actions:[^\[]*(\[.*\])"
    ANSWER_PATTERN = r"(?s)^Answer:\s?([\s\S]*)$"

    thought: Optional[str] = field(default=None, kw_only=True)
    actions: list[ToolAction] = field(factory=list, kw_only=True)
    answer: Optional[str] = field(default=None, kw_only=True)
    output: Optional[BaseArtifact] = field(default=None, init=False)
    generate_assistant_subtask_template: Callable[[BaseSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_assistant_subtask_template, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[BaseSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_user_subtask_template, takes_self=True),
        kw_only=True,
    )
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)
    _input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
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

    def attach_to(self, parent_task: BaseTask) -> BaseSubtask:
        subtask = super().attach_to(parent_task)

        try:
            if isinstance(self.input, TextArtifact):
                self.__init_from_prompt(self.input.to_text())
            else:
                self.__init_from_artifacts(self.input)
        except Exception as e:
            logger.error("Subtask %s\nError parsing tool action: %s", self.origin_task.id, e)

            raise ValueError(f"ToolAction input parsing error: {e}") from e

        return subtask

    def before_run(self) -> None:
        EventBus.publish_event(
            StartActionsSubtaskEvent(
                task_id=self.id,
                task_parent_ids=self.parent_ids,
                task_child_ids=self.child_ids,
                task_input=self.input,
                task_output=self.output,
                subtask_parent_task_id=self.origin_task.id,
                subtask_thought=self.thought,
                subtask_actions=self.actions_to_dicts(),
            ),
        )

        parts = [
            f"ActionsSubtask {self.id}",
            *([f"\nThought: {self.thought}"] if self.thought else []),
            f"\nActions: {self.actions_to_json()}" if self.actions else "",
            f"\nAnswer: {self.answer}" if self.answer else "",
        ]
        logger.info("".join(parts))

    def should_run(self) -> bool:
        return len(self.actions) > 0

    def try_run(self) -> BaseArtifact:
        try:
            if self.answer is not None:
                return TextArtifact(self.answer)
            elif any(isinstance(a.output, ErrorArtifact) for a in self.actions):
                errors = [a.output.value for a in self.actions if isinstance(a.output, ErrorArtifact)]

                return ErrorArtifact("\n\n".join(errors))
            else:
                results = self.run_actions(self.actions)

                actions_output = []
                for result in results:
                    tag, output = result
                    output.name = f"{tag} output"

                    actions_output.append(output)
                return ListArtifact(actions_output)
        except Exception as e:
            logger.exception("Subtask %s\n%s", self.id, e)

            return ErrorArtifact(str(e), exception=e)

    def run_actions(self, actions: list[ToolAction]) -> list[tuple[str, BaseArtifact]]:
        return utils.execute_futures_list(
            [self.futures_executor.submit(with_contextvars(self.run_action), a) for a in actions]
        )

    def run_action(self, action: ToolAction) -> tuple[str, BaseArtifact]:
        if action.tool is not None:
            if action.path is not None:
                output = action.tool.run(getattr(action.tool, action.path), self, action)
            else:
                output = ErrorArtifact("action path not found")
        else:
            output = ErrorArtifact("action name not found")
        action.output = output

        return action.tag, output

    def after_run(self) -> None:
        response = self.output.to_text() if isinstance(self.output, BaseArtifact) else str(self.output)

        EventBus.publish_event(
            FinishActionsSubtaskEvent(
                task_id=self.id,
                task_parent_ids=self.parent_ids,
                task_child_ids=self.child_ids,
                task_input=self.input,
                task_output=self.output,
                subtask_parent_task_id=self.origin_task.id,
                subtask_thought=self.thought,
                subtask_actions=self.actions_to_dicts(),
            ),
        )
        logger.info("ActionsSubtask %s\nResponse: %s", self.id, response)

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

    def to_text(self) -> str:
        return self.actions_to_json()

    def default_generate_assistant_subtask_template(self, subtask: BaseSubtask) -> str:
        return J2("tasks/toolkit_task/assistant_subtask.j2").render(
            stop_sequence=self.response_stop_sequence,
            subtask=subtask,
        )

    def default_generate_user_subtask_template(self, subtask: BaseSubtask) -> str:
        return J2("tasks/toolkit_task/user_subtask.j2").render(
            stop_sequence=self.response_stop_sequence,
            subtask=subtask,
        )

    def add_to_prompt_stack(self, prompt_driver: BasePromptDriver, prompt_stack: PromptStack) -> None:
        if prompt_driver.use_native_tools:
            action_calls = [
                ToolAction(name=action.name, path=action.path, tag=action.tag, input=action.input)
                for action in self.actions
            ]
            action_results = [
                ToolAction(
                    name=action.name,
                    path=action.path,
                    tag=action.tag,
                    output=action.output if action.output is not None else self.output,
                )
                for action in self.actions
            ]

            prompt_stack.add_assistant_message(
                ListArtifact(
                    [
                        *([TextArtifact(self.thought)] if self.thought else []),
                        *[ActionArtifact(a) for a in action_calls],
                    ],
                ),
            )
            prompt_stack.add_user_message(
                ListArtifact(
                    [
                        *[ActionArtifact(a) for a in action_results],
                        *([] if self.output else [TextArtifact("Please keep going")]),
                    ],
                ),
            )
        else:
            prompt_stack.add_assistant_message(self.generate_assistant_subtask_template(self))
            prompt_stack.add_user_message(self.generate_user_subtask_template(self))

    def _process_task_input(
        self,
        task_input: Union[str, tuple, list, BaseArtifact, Callable[[BaseTask], BaseArtifact]],
    ) -> Union[TextArtifact, ListArtifact]:
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

        self.actions = self.__parse_actions(actions_matches)

        if thought_matches:
            self.thought = thought_matches[-1]

        if not self.actions and self.output is None:
            if answer_matches:
                # A direct answer is provided, set it as the output.
                self.answer = answer_matches[-1]
            else:
                # The LLM failed to follow the ReAct prompt, set the LLM's raw response as the output.
                self.answer = value

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

        # When parsing from Artifacts we can't determine the thought unless there are also Actions
        if self.actions:
            thoughts = [artifact.value for artifact in artifacts.value if isinstance(artifact, TextArtifact)]
            if thoughts:
                self.thought = thoughts[0]
        else:
            if self.answer is None:
                self.answer = artifacts.to_text()

    def __parse_actions(self, actions_matches: list[str]) -> list[ToolAction]:
        if len(actions_matches) == 0:
            return []
        try:
            data = actions_matches[-1]
            actions_list: list[dict] = json.loads(data, strict=False)

            return [self.__process_action_object(action_object) for action_object in actions_list]
        except json.JSONDecodeError as e:
            logger.exception("Subtask %sk\nInvalid actions JSON: %s", self.origin_task.id, e)

            raise ValueError(f"Actions JSON decoding error: {e}") from e

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
            raise Exception("ActionsSubtask must be attached to a Task that implements ActionsSubtaskOriginMixin.")

        action = ToolAction(tag=action_tag, name=action_name, path=action_path, input=action_input, tool=tool)

        self.__validate_action(action)

        return action

    def __validate_action(self, action: ToolAction) -> None:
        try:
            if action.tool is not None:
                if action.path is not None:
                    activity = getattr(action.tool, action.path)
                else:
                    raise Exception("ToolAction path not found.")

                if activity is not None:
                    activity_schema = action.tool.activity_schema(activity)
                else:
                    raise Exception("Activity not found.")

                if activity_schema is not None and action.input is not None:
                    activity_schema.validate(action.input)
        except schema.SchemaError as e:
            logger.exception("Subtask %s\nInvalid action JSON: %s", self.origin_task.id, e)

            action.output = ErrorArtifact(f"Activity input JSON validation error: {e}", exception=e)
        except SyntaxError as e:
            logger.exception("Subtask %s\nSyntax error: %s", self.origin_task.id, e)

            action.output = ErrorArtifact(f"Syntax error: {e}", exception=e)
