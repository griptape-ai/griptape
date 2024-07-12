from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable, Optional

from attrs import Attribute, Factory, define, field

from griptape import utils
from griptape.artifacts import ActionArtifact, BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack, ToolAction
from griptape.mixins import ActionsSubtaskOriginMixin
from griptape.tasks import ActionsSubtask, PromptTask
from griptape.utils import J2

if TYPE_CHECKING:
    from schema import Schema

    from griptape.memory import TaskMemory
    from griptape.structures import Structure
    from griptape.tools import BaseTool


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
    generate_assistant_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_assistant_subtask_template_generator, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[ActionsSubtask], str] = field(
        default=Factory(lambda self: self.default_user_subtask_template_generator, takes_self=True),
        kw_only=True,
    )
    response_stop_sequence: str = field(default=RESPONSE_STOP_SEQUENCE, kw_only=True)

    def __attrs_post_init__(self) -> None:
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
        memory = self.structure.conversation_memory

        stack.add_system_message(self.generate_system_template(self))

        stack.add_user_message(self.input)

        if self.output:
            stack.add_assistant_message(self.output.to_text())
        else:
            for s in self.subtasks:
                if self.prompt_driver.use_native_tools:
                    action_calls = [
                        ToolAction(name=action.name, path=action.path, tag=action.tag, input=action.input)
                        for action in s.actions
                    ]
                    action_results = [
                        ToolAction(name=action.name, path=action.path, tag=action.tag, output=action.output)
                        for action in s.actions
                    ]

                    stack.add_assistant_message(
                        ListArtifact(
                            [
                                *([TextArtifact(s.thought)] if s.thought else []),
                                *[ActionArtifact(a) for a in action_calls],
                            ],
                        ),
                    )
                    stack.add_user_message(
                        ListArtifact(
                            [
                                *[ActionArtifact(a) for a in action_results],
                                *([] if s.output else [TextArtifact("Please keep going")]),
                            ],
                        ),
                    )
                else:
                    stack.add_assistant_message(self.generate_assistant_subtask_template(s))
                    stack.add_user_message(self.generate_user_subtask_template(s))

        if memory:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_prompt_stack(stack, 1)

        return stack

    def preprocess(self, structure: Structure) -> ToolkitTask:
        super().preprocess(structure)

        if self.task_memory is None and structure.task_memory:
            self.set_default_tools_memory(structure.task_memory)

        return self

    def default_system_template_generator(self, _: PromptTask) -> str:
        schema = self.actions_schema().json_schema("Actions Schema")
        schema["minItems"] = 1  # The `schema` library doesn't support `minItems` so we must add it manually.

        return J2("tasks/toolkit_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets),
            action_names=str.join(", ", [tool.name for tool in self.tools]),
            actions_schema=utils.minify_json(json.dumps(schema)),
            meta_memory=J2("memory/meta/meta_memory.j2").render(meta_memories=self.meta_memories),
            use_native_tools=self.prompt_driver.use_native_tools,
            stop_sequence=self.response_stop_sequence,
        )

    def default_assistant_subtask_template_generator(self, subtask: ActionsSubtask) -> str:
        return J2("tasks/toolkit_task/assistant_subtask.j2").render(
            stop_sequence=self.response_stop_sequence,
            subtask=subtask,
        )

    def default_user_subtask_template_generator(self, subtask: ActionsSubtask) -> str:
        return J2("tasks/toolkit_task/user_subtask.j2").render(
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

    def run(self) -> BaseArtifact:
        from griptape.tasks import ActionsSubtask

        self.subtasks.clear()

        if self.response_stop_sequence not in self.prompt_driver.tokenizer.stop_sequences:
            self.prompt_driver.tokenizer.stop_sequences.extend([self.response_stop_sequence])

        result = self.prompt_driver.run(self.prompt_stack)
        subtask = self.add_subtask(ActionsSubtask(result.to_artifact()))

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

                    result = self.prompt_driver.run(prompt_stack=self.prompt_stack)
                    subtask = self.add_subtask(ActionsSubtask(result.to_artifact()))
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
