from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Callable, Optional, Union

from attrs import NOTHING, Attribute, Factory, NothingType, define, field
from pydantic import BaseModel
from schema import Schema

from griptape import utils
from griptape.artifacts import (
    AudioArtifact,
    BaseArtifact,
    ErrorArtifact,
    GenericArtifact,
    JsonArtifact,
    ListArtifact,
    ModelArtifact,
    TextArtifact,
)
from griptape.common import PromptStack
from griptape.configs import Defaults
from griptape.memory.structure import Run
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.mixins.rule_mixin import RuleMixin
from griptape.rules import Ruleset
from griptape.tasks import ActionsSubtask, BaseSubtask, BaseTask, OutputSchemaValidationSubtask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers.prompt import BasePromptDriver
    from griptape.memory import TaskMemory
    from griptape.memory.structure.base_conversation_memory import BaseConversationMemory
    from griptape.structures import Structure
    from griptape.tools import BaseTool

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class PromptTask(
    BaseTask[Union[TextArtifact, AudioArtifact, GenericArtifact, JsonArtifact, ListArtifact, ErrorArtifact]],
    RuleMixin,
    ActionsSubtaskOriginMixin,
):
    DEFAULT_MAX_STEPS = 20
    # Stop sequence for chain-of-thought in the framework. Using this "token-like" string to make it more unique,
    # so that it doesn't trigger on accident.
    RESPONSE_STOP_SEQUENCE = "<|Response|>"
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: Defaults.drivers_config.prompt_driver), kw_only=True, metadata={"serializable": True}
    )
    output_schema: Optional[Union[Schema, type[BaseModel]]] = field(default=None, kw_only=True)
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_generate_system_template, takes_self=True),
        kw_only=True,
    )
    _conversation_memory: Union[Optional[BaseConversationMemory], NothingType] = field(
        default=Factory(lambda: NOTHING), kw_only=True, alias="conversation_memory"
    )
    _input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
        alias="input",
    )
    tools: list[BaseTool] = field(factory=list, kw_only=True, metadata={"serializable": True})
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True, metadata={"serializable": True})
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)
    subtasks: list[BaseSubtask] = field(factory=list)
    generate_assistant_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_assistant_subtask_template, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_user_subtask_template, takes_self=True),
        kw_only=True,
    )
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)
    reflect_on_tool_use: bool = field(default=True, kw_only=True)
    subtask_runners: list[Callable[[BaseArtifact], BaseArtifact]] = field(
        default=Factory(
            lambda self: [self.default_run_actions_subtasks, self.default_run_output_schema_validation_subtasks],
            takes_self=True,
        ),
        kw_only=True,
    )

    @property
    def rulesets(self) -> list:
        default_rules = self.rules
        rulesets = self._rulesets.copy()

        if self.structure is not None:
            if self.structure._rulesets:
                rulesets = self.structure._rulesets + self._rulesets
            if self.structure.rules:
                default_rules = self.structure.rules + self.rules

        if default_rules:
            rulesets.append(Ruleset(name=self.DEFAULT_RULESET_NAME, rules=default_rules))

        return rulesets

    @property
    def input(self) -> BaseArtifact:
        return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    @property
    def conversation_memory(self) -> Optional[BaseConversationMemory]:
        if self._conversation_memory is NOTHING:
            if self.structure is None:
                return None
            return self.structure.conversation_memory
        return self._conversation_memory

    @conversation_memory.setter
    def conversation_memory(self, value: Optional[BaseConversationMemory]) -> None:
        self._conversation_memory = value

    @property
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack(tools=self.tools, output_schema=self.output_schema)
        memory = self.conversation_memory

        system_template = self.generate_system_template(self)
        if system_template:
            stack.add_system_message(system_template)

        stack.add_user_message(self.input)

        if self.output:
            stack.add_assistant_message(self.output.to_text())
        else:
            for s in self.subtasks:
                s.add_to_prompt_stack(stack)

        if memory is not None:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_prompt_stack(self.prompt_driver, stack, 1 if system_template else 0)

        return stack

    @property
    def tool_output_memory(self) -> list[TaskMemory]:
        unique_memory_dict = {}

        for memories in [tool.output_memory for tool in self.tools if tool.output_memory]:
            for memory_list in memories.values():
                for memory in memory_list:
                    if memory.name not in unique_memory_dict:
                        unique_memory_dict[memory.name] = memory

        return list(unique_memory_dict.values())

    @tools.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_tools(self, _: Attribute, tools: list[BaseTool]) -> None:
        tool_names = [t.name for t in tools]

        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tools names have to be unique in task")

    @output_schema.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_output_schema(self, _: Attribute, output_schema: Optional[Union[Schema, type[BaseModel]]]) -> None:
        if (
            output_schema is None
            or isinstance(self.output_schema, Schema)
            or (isinstance(self.output_schema, type) and issubclass(self.output_schema, BaseModel))
        ):
            return
        raise ValueError(f"Unsupported output schema type: {type(self.output_schema)}")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if self.task_memory:
            self.set_default_tools_memory(self.task_memory)

    output: Optional[BaseArtifact] = field(default=None, init=False)

    def before_run(self) -> None:
        super().before_run()

        logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        logger.info(
            "%s %s\nOutput: %s",
            self.__class__.__name__,
            self.id,
            self.output.to_text() if self.output is not None else "",
        )
        conversation_memory = self.conversation_memory
        if (
            (self.structure is None or self.structure.conversation_memory_strategy == "per_task")
            and conversation_memory is not None
            and self.output is not None
        ):
            run = Run(input=self.input, output=self.output)

            conversation_memory.add_run(run)

    def try_run(self) -> ListArtifact | TextArtifact | AudioArtifact | GenericArtifact | JsonArtifact | ErrorArtifact:
        self.subtasks.clear()
        if self.response_stop_sequence not in self.prompt_driver.tokenizer.stop_sequences:
            self.prompt_driver.tokenizer.stop_sequences.extend([self.response_stop_sequence])

        output = self.prompt_driver.run(self.prompt_stack).to_artifact(
            meta={"is_react_prompt": not self.prompt_driver.use_native_tools}
        )
        for subtask_runner in self.subtask_runners:
            output = subtask_runner(output)

        if isinstance(output, (ListArtifact, TextArtifact, AudioArtifact, JsonArtifact, ModelArtifact, ErrorArtifact)):
            return output
        raise ValueError(f"Unsupported output type: {type(output)}")

    def preprocess(self, structure: Structure) -> BaseTask:
        super().preprocess(structure)

        if self.task_memory is None and structure.task_memory:
            self.set_default_tools_memory(structure.task_memory)

        return self

    def default_generate_system_template(self, _: PromptTask) -> str:
        schema = self.actions_schema().json_schema("Actions Schema")
        schema["minItems"] = 1  # The `schema` library doesn't support `minItems` so we must add it manually.

        return J2("tasks/prompt_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.rulesets),
            action_names=str.join(", ", [tool.name for tool in self.tools]),
            actions_schema=utils.minify_json(json.dumps(schema)),
            meta_memory=J2("memory/meta/meta_memory.j2").render(meta_memories=self.meta_memories),
            use_native_tools=self.prompt_driver.use_native_tools,
            stop_sequence=self.response_stop_sequence,
            reflect_on_tool_use=self.reflect_on_tool_use,
        )

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

    def actions_schema(self) -> Schema:
        return self._actions_schema_for_tools(self.tools)

    def set_default_tools_memory(self, memory: TaskMemory) -> None:
        self.task_memory = memory

        for tool in self.tools:
            if self.task_memory:
                if tool.input_memory is None:
                    tool.input_memory = [self.task_memory]
                if tool.output_memory is None and tool.off_prompt:
                    tool.output_memory = {getattr(a, "name"): [self.task_memory] for a in tool.activities()}

    def find_subtask(self, subtask_id: str) -> BaseSubtask:
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                return subtask
        raise ValueError(f"Subtask with id {subtask_id} not found.")

    def add_subtask(self, subtask: BaseSubtask) -> BaseSubtask:
        subtask.attach_to(self)
        subtask.structure = self.structure

        if len(self.subtasks) > 0:
            self.subtasks[-1].add_child(subtask)
            subtask.add_parent(self.subtasks[-1])

        self.subtasks.append(subtask)

        return subtask

    def find_tool(self, tool_name: str) -> BaseTool:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        raise ValueError(f"Tool with name {tool_name} not found.")

    def find_memory(self, memory_name: str) -> TaskMemory:
        for memory in self.tool_output_memory:
            if memory.name == memory_name:
                return memory
        raise ValueError(f"Memory with name {memory_name} not found.")

    def default_run_actions_subtasks(self, subtask_input: BaseArtifact) -> BaseArtifact:
        if not self.tools:
            return subtask_input
        subtask = self.add_subtask(
            ActionsSubtask(
                subtask_input,
                # TODO: Remove these fields in Prompt Task in Griptape 2.0
                generate_user_subtask_template=self.generate_user_subtask_template,
                generate_assistant_subtask_template=self.generate_assistant_subtask_template,
                response_stop_sequence=self.response_stop_sequence,
            )
        )

        while subtask.output is None:
            if len(self.subtasks) >= self.max_subtasks:
                subtask.output = ErrorArtifact(f"Exceeded tool limit of {self.max_subtasks} subtasks per task")
            else:
                subtask.run()

                if self.reflect_on_tool_use:
                    output = self.prompt_driver.run(self.prompt_stack).to_artifact(
                        meta={"is_react_prompt": not self.prompt_driver.use_native_tools}
                    )
                    subtask = self.add_subtask(ActionsSubtask(output))

        return subtask.output

    def default_run_output_schema_validation_subtasks(self, subtask_input: BaseArtifact) -> BaseArtifact:
        if self.output_schema is None:
            return subtask_input
        subtask = self.add_subtask(OutputSchemaValidationSubtask(subtask_input, output_schema=self.output_schema))

        while subtask.output is None:
            if len(self.subtasks) >= self.max_subtasks:
                subtask.output = ErrorArtifact(f"Exceeded tool limit of {self.max_subtasks} subtasks per task")
            else:
                subtask.run()

                output = subtask.output
                output = self.prompt_driver.run(self.prompt_stack).to_artifact(
                    meta={"is_react_prompt": not self.prompt_driver.use_native_tools}
                )
                subtask = self.add_subtask(OutputSchemaValidationSubtask(output, output_schema=self.output_schema))

        return subtask.output

    def _process_task_input(
        self,
        task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact],
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            return TextArtifact(J2().render_from_string(task_input.value, **self.full_context), meta=task_input.meta)
        if isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        if isinstance(task_input, ListArtifact):
            return ListArtifact([self._process_task_input(elem) for elem in task_input.value])
        if isinstance(task_input, BaseArtifact):
            return task_input
        if isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        return self._process_task_input(TextArtifact(task_input))
