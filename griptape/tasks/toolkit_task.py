from __future__ import annotations
import json
from typing import TYPE_CHECKING, Callable, Optional
from attrs import define, field, Factory
from schema import Schema

from griptape import utils
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.mixins import ActionsSubtaskOriginMixin
from griptape.tasks import ActionsSubtask
from griptape.tasks import PromptTask
from griptape.utils import J2
from griptape.utils import PromptStack

if TYPE_CHECKING:
    from griptape.tools import BaseTool
    from griptape.memory import TaskMemory
    from griptape.structures import Structure


@define
class ToolkitTask(PromptTask, ActionsSubtaskOriginMixin):
    DEFAULT_MAX_STEPS = 20
    # Stop sequence for chain-of-thought in the framework. Using this "token-like" string to make it more unique,
    # so that it doesn't trigger on accident.
    RESPONSE_STOP_SEQUENCE = "<|Response|>"

    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_subtasks: int = field(default=DEFAULT_MAX_STEPS, kw_only=True)
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)
    subtasks: list[ActionsSubtask] = field(factory=list)
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)
    system_template_path: str = field(default="tasks/toolkit_task/system.j2", kw_only=True)
    assistant_template_path: str = field(default="tasks/toolkit_task/assistant_subtask.j2", kw_only=True)
    user_template_path: str = field(default="tasks/toolkit_task/user_subtask.j2", kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.task_memory:
            self.set_default_tools_memory(self.task_memory)

    @tools.validator  # pyright: ignore
    def validate_tools(self, _, tools: list[BaseTool]) -> None:
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
        stack = PromptStack()
        memory = self.structure.conversation_memory

        stack.add_system_input(self.generate_system_template())

        stack.add_user_input(self.input.to_text())

        if self.output:
            stack.add_assistant_input(self.output.to_text())
        else:
            for s in self.subtasks:
                stack.add_assistant_input(
                    self.render_template(
                        self.assistant_template_path, stop_sequence=self.response_stop_sequence, subtask=s
                    )
                )
                stack.add_user_input(self.render_user_template(stop_sequence=self.response_stop_sequence, subtask=s))

        if memory:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_prompt_stack(stack, 1)

        return stack

    def preprocess(self, structure: Structure) -> ToolkitTask:
        super().preprocess(structure)

        if self.task_memory is None and structure.task_memory:
            self.set_default_tools_memory(structure.task_memory)

        return self

    def generate_system_template(self) -> str:
        schema = self.actions_schema().json_schema("Actions Schema")
        schema["minItems"] = 1  # The `schema` library doesn't support `minItems` so we must add it manually.

        return self.render_system_template(
            rulesets=self.render_rulesets_template(rulesets=self.all_rulesets),
            action_names=str.join(", ", [tool.name for tool in self.tools]),
            actions_schema=utils.minify_json(json.dumps(schema)),
            meta_memory=self.render_meta_memory_template(meta_memories=self.meta_memories),
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

    def run(self) -> BaseArtifact:
        from griptape.tasks import ActionsSubtask

        self.subtasks.clear()

        self.prompt_driver.tokenizer.stop_sequences.extend([self.response_stop_sequence])
        subtask = self.add_subtask(ActionsSubtask(self.prompt_driver.run(prompt_stack=self.prompt_stack).to_text()))

        while True:
            if subtask.output is None:
                if len(self.subtasks) >= self.max_subtasks:
                    subtask.output = ErrorArtifact(f"Exceeded tool limit of {self.max_subtasks} subtasks per task")
                elif not subtask.actions:
                    # handle case when the LLM failed to follow the ReAct prompt and didn't return a proper action
                    subtask.output = subtask.input
                else:
                    subtask.before_run()
                    subtask.run()
                    subtask.after_run()

                    subtask = self.add_subtask(
                        ActionsSubtask(self.prompt_driver.run(prompt_stack=self.prompt_stack).to_text())
                    )
            else:
                break

        self.output = subtask.output

        return self.output

    def find_subtask(self, subtask_id: str) -> ActionsSubtask:
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                return subtask
        raise ValueError(f"Subtask with id {subtask_id} not found.")

    def add_subtask(self, subtask: ActionsSubtask) -> ActionsSubtask:
        subtask.attach_to(self)

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
