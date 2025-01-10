from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Callable, Optional, Union

from attrs import NOTHING, Attribute, Factory, NothingType, define, field
from schema import Literal, Schema

from griptape import utils
from griptape.artifacts import ActionArtifact, BaseArtifact, ErrorArtifact, JsonArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack, ToolAction
from griptape.configs import Defaults
from griptape.memory.structure import Run
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.mixins.rule_mixin import RuleMixin
from griptape.rules import Ruleset
from griptape.tasks import ActionsSubtask, BaseSubtask, BaseTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.memory import TaskMemory
    from griptape.memory.structure.base_conversation_memory import BaseConversationMemory
    from griptape.structures import Structure
    from griptape.tools import BaseTool

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class PromptTask(BaseTask, RuleMixin, ActionsSubtaskOriginMixin):
    DEFAULT_MAX_STEPS = 20
    # Stop sequence for chain-of-thought in the framework. Using this "token-like" string to make it more unique,
    # so that it doesn't trigger on accident.
    RESPONSE_STOP_SEQUENCE = "<|Response|>"
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: Defaults.drivers_config.prompt_driver), kw_only=True, metadata={"serializable": True}
    )
    output_schema: Optional[Schema] = field(default=None, kw_only=True)
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_generate_system_template, takes_self=True),
        kw_only=True,
    )
    conversation_memory: Union[Optional[BaseConversationMemory], NothingType] = field(
        default=Factory(lambda: NOTHING), kw_only=True
    )
    _input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
        alias="input",
    )
    tools: list[BaseTool] = field(factory=list, kw_only=True, metadata={"serializable": True})
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True, metadata={"serializable": True})
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)
    subtasks: list[BaseSubtask] = field(factory=list)
    generate_assistant_subtask_template: Callable[[BaseSubtask], Union[str, BaseArtifact]] = field(
        default=Factory(lambda self: self.default_generate_assistant_subtask_template, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[BaseSubtask], Union[str, BaseArtifact]] = field(
        default=Factory(lambda self: self.default_generate_user_subtask_template, takes_self=True),
        kw_only=True,
    )
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)

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
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack(tools=self.tools, output_schema=self.output_schema)
        memory = self.structure.conversation_memory if self.structure is not None else None

        system_template = self.generate_system_template(self)
        if system_template:
            stack.add_system_message(system_template)

        stack.add_user_message(self.input)

        if self.output:
            stack.add_assistant_message(self.output.to_text())
        else:
            for s in self.subtasks:
                stack.add_assistant_message(self.generate_assistant_subtask_template(s))
                stack.add_user_message(self.generate_user_subtask_template(s))

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
            and conversation_memory is not NOTHING
            and self.output is not None
        ):
            run = Run(input=self.input, output=self.output)

            conversation_memory.add_run(run)

    def try_run(self) -> BaseArtifact:
        from griptape.tasks.schema_validation_subtask import SchemaValidationSubtask

        self.subtasks.clear()

        if self.response_stop_sequence not in self.prompt_driver.tokenizer.stop_sequences:
            self.prompt_driver.tokenizer.stop_sequences.extend([self.response_stop_sequence])

        output = self.prompt_driver.run(self.prompt_stack).to_artifact()

        if isinstance(output, TextArtifact):
            if self.output_schema is not None:
                output_schema = self.output_schema
                output = self._run_subtasks(
                    lambda result: SchemaValidationSubtask(input=result, schema=output_schema),
                    output,
                    lambda artifact: isinstance(artifact, ErrorArtifact),
                )
                if not isinstance(output, ErrorArtifact) and self.prompt_driver.structured_output_strategy in (
                    "native",
                    "rule",
                ):
                    output = JsonArtifact(output.value)
            # This could be a problem if the user has use_native_tools=False and output_schema set
            elif self.tools:
                output = self._run_subtasks(lambda result: ActionsSubtask(result), output, lambda _: True)
        elif (
            isinstance(output, ActionArtifact)
            or (isinstance(output, ListArtifact) and output.has_type(ActionArtifact))
            and self.tools
        ):
            output = self._run_subtasks(lambda result: ActionsSubtask(result), output, lambda _: True)

        return output

    def preprocess(self, structure: Structure) -> BaseTask:
        super().preprocess(structure)

        if self.conversation_memory is NOTHING:
            if structure.conversation_memory is not None:
                self.conversation_memory = structure.conversation_memory
            else:
                self.conversation_memory = None

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
        )

    def default_generate_assistant_subtask_template(self, subtask: BaseSubtask) -> str | BaseArtifact:
        if isinstance(subtask, ActionsSubtask):
            if self.prompt_driver.use_native_tools:
                action_calls = [
                    ToolAction(name=action.name, path=action.path, tag=action.tag, input=action.input)
                    for action in subtask.actions
                ]
                return ListArtifact(
                    [
                        *([TextArtifact(subtask.thought)] if subtask.thought else []),
                        *[ActionArtifact(a) for a in action_calls],
                    ],
                )
            else:
                return J2("tasks/prompt_task/assistant_subtask.j2").render(
                    stop_sequence=self.response_stop_sequence,
                    subtask=subtask,
                )
        else:
            return subtask.input

    def default_generate_user_subtask_template(self, subtask: BaseSubtask) -> str | BaseArtifact:
        if isinstance(subtask, ActionsSubtask):
            if self.prompt_driver.use_native_tools:
                action_results = [
                    ToolAction(
                        name=action.name,
                        path=action.path,
                        tag=action.tag,
                        output=action.output if action.output is not None else subtask.output,
                    )
                    for action in subtask.actions
                ]
                return ListArtifact(
                    [
                        *[ActionArtifact(a) for a in action_results],
                        *([] if subtask.output else [TextArtifact("Please keep going")]),
                    ],
                )
            else:
                return J2("tasks/prompt_task/user_subtask.j2").render(
                    stop_sequence=self.response_stop_sequence,
                    subtask=subtask,
                )
        else:
            return f"Correct your JSON output with this error feedback: {subtask.output}"

    def actions_schema(self) -> Schema:
        action_schemas = []

        for tool in self.tools:
            for activity_schema in tool.activity_schemas():
                action_schema = activity_schema.schema
                tag_key = Literal("tag", description="Unique tag name for action execution.")

                action_schema[tag_key] = str

                action_schemas.append(action_schema)

        return Schema(description="JSON schema for an array of actions.", schema=action_schemas)

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

    def _run_subtasks(
        self,
        subtask_factory: Callable[[BaseArtifact], BaseSubtask],
        initial_input: BaseArtifact,
        more_work: Callable[[BaseArtifact], bool],
    ) -> BaseArtifact:
        subtask = self.add_subtask(subtask_factory(initial_input))
        while True:
            if subtask.output is None:
                if len(self.subtasks) >= self.max_subtasks:
                    return ErrorArtifact(f"Exceeded tool limit of {self.max_subtasks} subtasks per task")
                else:
                    output = subtask.run()

                    # CoT: work until the output is a non-tool call
                    # non-CoT: work until the output is not an error
                    # Validation: work until the output is not an error
                    # Unknown: always give me the result with no subtasks
                    # Should this be a enum? Or a callable?
                    if more_work(output):
                        result = self.prompt_driver.run(self.prompt_stack).to_artifact()
                        subtask = self.add_subtask(subtask_factory(result))
            else:
                break

        return subtask.output

    def _process_task_input(
        self,
        task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact],
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, ListArtifact):
            return ListArtifact([self._process_task_input(elem) for elem in task_input.value])
        elif isinstance(task_input, BaseArtifact):
            return task_input
        elif isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            return self._process_task_input(TextArtifact(task_input))
