from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from attrs import Attribute, Factory, define, field

from griptape import utils
from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.common import PromptStack
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks import PromptTask
from griptape.tasks.actions_subtask import ActionsSubtask
from griptape.tasks.eval_subtask import EvalSubtask
from griptape.utils import J2

if TYPE_CHECKING:
    from schema import Schema

    from griptape.memory import TaskMemory
    from griptape.structures import Structure
    from griptape.tasks.base_subtask import BaseSubtask
    from griptape.tools import BaseTool


@define
class ToolkitTask(PromptTask, ActionsSubtaskOriginMixin):
    # Stop sequence for chain-of-thought in the framework. Using this "token-like" string to make it more unique,
    # so that it doesn't trigger on accident.
    RESPONSE_STOP_SEQUENCE = "<|Response|>"
    DEFAULT_MAX_STEPS = 20

    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)
    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)
    subtasks: list[BaseSubtask] = field(factory=list)
    subtask_pipeline: list[type[BaseSubtask]] = field(
        default=Factory(lambda: [ActionsSubtask, EvalSubtask]), kw_only=True
    )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if self.task_memory:
            self.set_default_tools_memory(self.task_memory)

    @tools.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_tools(self, _: Attribute, tools: list[BaseTool]) -> None:
        tool_names = [t.name for t in tools]

        if len(tool_names) > len(set(tool_names)):
            raise ValueError("tools names have to be unique in task")

    @property
    def tool_output_memory(self) -> list[TaskMemory]:
        unique_memory_dict = {}

        for memories in [tool.output_memory for tool in self.tools if tool.output_memory]:
            for memory_list in memories.values():
                for memory in memory_list:
                    if memory.name not in unique_memory_dict:
                        unique_memory_dict[memory.name] = memory

        return list(unique_memory_dict.values())

    @property
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack(tools=self.tools)
        memory = self.structure.conversation_memory if self.structure is not None else None

        stack.add_system_message(self.generate_system_template(self))

        stack.add_user_message(self.input)

        if self.output is not None:
            stack.add_assistant_message(self.output.to_text())
        else:
            for s in self.subtasks:
                s.add_to_prompt_stack(self.prompt_driver, stack)

        if memory is not None:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_prompt_stack(self.prompt_driver, stack, 1)

        return stack

    def preprocess(self, structure: Structure) -> ToolkitTask:
        super().preprocess(structure)

        if self.task_memory is None and structure.task_memory:
            self.set_default_tools_memory(structure.task_memory)

        return self

    def default_generate_system_template(self, _: PromptTask) -> str:
        schema = self.actions_schema().json_schema("Actions Schema")
        schema["minItems"] = 1  # The `schema` library doesn't support `minItems` so we must add it manually.

        return J2("tasks/toolkit_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.rulesets),
            action_names=str.join(", ", [tool.name for tool in self.tools]),
            actions_schema=utils.minify_json(json.dumps(schema)),
            meta_memory=J2("memory/meta/meta_memory.j2").render(meta_memories=self.meta_memories),
            use_native_tools=self.prompt_driver.use_native_tools,
            stop_sequence=self.response_stop_sequence,
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

    def try_run(self) -> BaseArtifact:
        self.subtasks.clear()

        if self.response_stop_sequence not in self.prompt_driver.tokenizer.stop_sequences:
            self.prompt_driver.tokenizer.stop_sequences.append(self.response_stop_sequence)

        result = self.prompt_driver.run(self.prompt_stack).to_artifact()

        while True:
            subtask_output = result
            for subtask_type in self.subtask_pipeline:
                subtask = subtask_type(subtask_output)
                subtask.attach_to(self)
                if subtask.should_run():
                    self.add_subtask(subtask)
                    subtask_output = subtask.run()
            # TODO: re-prompting the LLM with ActionsSubtask output yield the LLM giving a useful answer that considers the Tool usage.
            # re-prompting the LLM with the EvalSubtask output yields an unhelpful "Thanks for the feedback" response.
            # Is that an issue with EvalSubtask or the overall loop?
            result = self.prompt_driver.run(self.prompt_stack).to_artifact()
            # Issue, how do we determine how to stop the loop?
            if (
                subtask_output is not None
                and not isinstance(subtask_output, (ErrorArtifact, InfoArtifact))
                and not (
                    isinstance(subtask_output, ListArtifact) and subtask_output.has_type((ErrorArtifact, InfoArtifact))
                )
            ):
                return subtask_output

    def find_subtask(self, subtask_id: str) -> BaseSubtask:
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                return subtask
        raise ValueError(f"Subtask with id {subtask_id} not found.")

    def add_subtask(self, subtask: BaseSubtask) -> BaseSubtask:
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
