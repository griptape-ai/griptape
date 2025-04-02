from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Callable, Optional, Union

from attrs import Factory, define, field

from griptape import utils
from griptape.artifacts import (
    ActionArtifact,
    AudioArtifact,
    BaseArtifact,
    ErrorArtifact,
    JsonArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.common import PromptStack, ToolAction
from griptape.configs import Defaults
from griptape.events import EventBus, FinishActionsSubtaskEvent, StartActionsSubtaskEvent
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks.base_subtask import BaseSubtask
from griptape.tools.structured_output.tool import StructuredOutputTool
from griptape.utils import J2, remove_null_values_in_dict_recursively, with_contextvars

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class ActionsSubtask(BaseSubtask[Union[ListArtifact, ErrorArtifact]]):
    THOUGHT_PATTERN = r"(?s)^Thought:\s*(.*?)$"
    ACTIONS_PATTERN = r"(?s)Actions:[^\[]*(\[.*\])"
    ANSWER_PATTERN = r"(?s)^Answer:\s?([\s\S]*)$"

    RESPONSE_STOP_SEQUENCE = "<|Response|>"

    thought: Optional[str] = field(default=None, kw_only=True)
    actions: list[ToolAction] = field(factory=list, kw_only=True)
    output: Optional[BaseArtifact] = field(default=None, init=False)
    generate_assistant_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_assistant_subtask_template, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_user_subtask_template, takes_self=True),
        kw_only=True,
    )
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)
    _input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
        alias="input",
    )
    _memory: Optional[TaskMemory] = None
    _origin_task: Optional[BaseTask] = field(default=None, kw_only=True)

    @property
    def input(self) -> TextArtifact | AudioArtifact | ListArtifact:
        return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    def attach_to(self, parent_task: BaseTask) -> None:
        super().attach_to(parent_task)
        self.structure = parent_task.structure

        task_input = self.input
        try:
            if isinstance(task_input, TextArtifact) and task_input.meta.get("is_react_prompt", False):
                self.__init_from_prompt(task_input.to_text())
            else:
                self.__init_from_artifact(task_input)

            # If StructuredOutputTool was used, treat the input to it as the output of the subtask.
            structured_outputs = [a for a in self.actions if isinstance(a.tool, StructuredOutputTool)]
            if structured_outputs:
                output_values = [JsonArtifact(a.input["values"]) for a in structured_outputs]
                if len(structured_outputs) > 1:
                    self.output = ListArtifact(output_values)
                else:
                    self.output = output_values[0]
        except Exception as e:
            logger.error("Subtask %s\nError parsing tool action: %s", self.origin_task.id, e)

            self.output = ErrorArtifact(f"ToolAction input parsing error: {e}", exception=e)

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
            f"{self.__class__.__name__} {self.id}",
            *([f"\nThought: {self.thought}"] if self.thought else []),
            f"\nActions: {self.actions_to_json()}",
        ]
        logger.info("".join(parts))

    def try_run(self) -> ListArtifact | ErrorArtifact:
        try:
            if any(isinstance(a.output, ErrorArtifact) for a in self.actions):
                errors = [a.output.value for a in self.actions if isinstance(a.output, ErrorArtifact)]

                self.output = ErrorArtifact("\n\n".join(errors))
            else:
                results = self.run_actions(self.actions)

                actions_output = []
                for result in results:
                    tag, output = result
                    output.name = f"{tag} output"

                    actions_output.append(output)
                self.output = ListArtifact(actions_output)
        except Exception as e:
            logger.debug("Subtask %s\n%s", self.id, e)

            self.output = ErrorArtifact(str(e), exception=e)
        if self.output is not None:
            return self.output
        return ErrorArtifact("no tool output")

    def run_actions(self, actions: list[ToolAction]) -> list[tuple[str, BaseArtifact]]:
        with self.create_futures_executor() as futures_executor:
            return utils.execute_futures_list(
                [futures_executor.submit(with_contextvars(self.run_action), a) for a in actions]
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
        logger.info("%s %s\nResponse: %s", self.__class__.__name__, self.id, response)

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

    def add_to_prompt_stack(self, stack: PromptStack) -> None:
        from griptape.tasks import PromptTask

        if isinstance(self.origin_task, PromptTask) and self.origin_task.prompt_driver.use_native_tools:
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

            stack.add_assistant_message(
                ListArtifact(
                    [
                        *([TextArtifact(self.thought)] if self.thought else []),
                        *[ActionArtifact(a) for a in action_calls],
                    ],
                ),
            )
            stack.add_user_message(
                ListArtifact(
                    [
                        *[ActionArtifact(a) for a in action_results],
                        *([] if self.output else [TextArtifact("Please keep going")]),
                    ],
                ),
            )
        else:
            stack.add_assistant_message(self.generate_assistant_subtask_template(self))
            stack.add_user_message(self.generate_user_subtask_template(self))

    def default_generate_assistant_subtask_template(self, subtask: ActionsSubtask) -> str:
        return J2("tasks/prompt_task/assistant_actions_subtask.j2").render(
            stop_sequence=self.response_stop_sequence,
            subtask=subtask,
        )

    def default_generate_user_subtask_template(self, subtask: ActionsSubtask) -> str:
        return J2("tasks/prompt_task/user_actions_subtask.j2").render(
            stop_sequence=self.response_stop_sequence,
            subtask=subtask,
        )

    def _process_task_input(
        self,
        task_input: Union[str, tuple, list, BaseArtifact, Callable[[BaseTask], BaseArtifact]],
    ) -> Union[TextArtifact, AudioArtifact, ListArtifact]:
        if isinstance(task_input, (TextArtifact, AudioArtifact, ListArtifact)):
            return task_input
        if isinstance(task_input, ActionArtifact):
            return ListArtifact([task_input])
        if isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        if isinstance(task_input, str):
            return self._process_task_input(TextArtifact(task_input))
        if isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
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
                self.output = TextArtifact(answer_matches[-1])
            else:
                # The LLM failed to follow the ReAct prompt, set the LLM's raw response as the output.
                self.output = TextArtifact(value)

    def __init_from_artifact(self, artifact: TextArtifact | AudioArtifact | ListArtifact) -> None:
        """Parses the input Artifact to extract either a final answer or thought and actions.

        When the input Artifact is a TextArtifact, it is assumed to be the final answer.
        When the input Artifact is a ListArtifact, it is assumed to contain both thought and actions.
        Text Artifacts are parsed as the thought, and ToolAction Artifacts parsed as the actions.

        Args:
            artifact: The input Artifacts.

        Returns:
            None
        """
        # When using native tools, we can assume that a TextArtifact or AudioArtifact is the LLM providing its final answer.
        if isinstance(artifact, (TextArtifact, AudioArtifact)):
            self.output = artifact
            return

        self.actions = [
            self.__process_action_object(artifact.value.to_dict())
            for artifact in artifact.value
            if isinstance(artifact, ActionArtifact)
        ]

        # When parsing from Artifacts we can't determine the thought unless there are also Actions
        if self.actions:
            thoughts = [artifact.value for artifact in artifact.value if isinstance(artifact, TextArtifact)]
            if thoughts:
                self.thought = thoughts[0]
        elif self.output is None:
            self.output = TextArtifact(artifact.to_text())

    def __parse_actions(self, actions_matches: list[str]) -> list[ToolAction]:
        if len(actions_matches) == 0:
            return []
        try:
            data = actions_matches[-1]
            actions_list: list[dict] = json.loads(data, strict=False)

            return [self.__process_action_object(action_object) for action_object in actions_list]
        except json.JSONDecodeError as e:
            logger.debug("Subtask %s\nInvalid actions JSON: %s", self.origin_task.id, e)

            self.output = ErrorArtifact(f"Actions JSON decoding error: {e}", exception=e)

            return []

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

        self.__validate_action(action)

        return action

    def __validate_action(self, action: ToolAction) -> None:
        if action.tool is None:
            return

        if action.path is None:
            raise Exception("ToolAction path not found.")
        activity = getattr(action.tool, action.path)

        if activity is None:
            raise Exception("Activity not found.")

        activity_schema = action.tool.activity_schema(activity)

        if activity_schema is None or action.input is None:
            return

        try:
            action.tool.validate_activity_schema(activity_schema, action.input)
        except ValueError as e:
            logger.debug("Subtask %s\nInvalid action JSON: %s", self.origin_task.id, e)

            action.output = ErrorArtifact(f"Activity input JSON validation error: {e}", exception=e)
