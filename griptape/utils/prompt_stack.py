from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from enum import Enum


from griptape.mixins import SerializableMixin
from griptape.tools.base_tool import BaseTool

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


@define
class PromptStack(SerializableMixin):
    class Role(Enum):
        GENERIC_ROLE = "generic"
        USER_ROLE = "user"
        ASSISTANT_ROLE = "assistant"
        SYSTEM_ROLE = "system"
        TOOL_ROLE = "tool"

    @define
    class Input(SerializableMixin):
        content: str = field(metadata={"serializable": True})
        role: PromptStack.Role = field(metadata={"serializable": True})

        def is_generic(self) -> bool:
            return self.role == PromptStack.Role.GENERIC_ROLE

        def is_system(self) -> bool:
            return self.role == PromptStack.Role.SYSTEM_ROLE

        def is_user(self) -> bool:
            return self.role == PromptStack.Role.USER_ROLE

        def is_assistant(self) -> bool:
            return self.role == PromptStack.Role.ASSISTANT_ROLE

        def is_tool(self) -> bool:
            return self.role == PromptStack.Role.TOOL_ROLE

    inputs: list[Input] = field(factory=list, kw_only=True, metadata={"serializable": True})
    tools: list[BaseTool] = field(factory=list, kw_only=True)

    def add_input(self, content: str, role: PromptStack.Role) -> Input:
        self.inputs.append(self.Input(content=content, role=role))

        return self.inputs[-1]

    def add_generic_input(self, content: str) -> Input:
        return self.add_input(content, PromptStack.Role.GENERIC_ROLE)

    def add_system_input(self, content: str) -> Input:
        return self.add_input(content, PromptStack.Role.SYSTEM_ROLE)

    def add_user_input(self, content: str) -> Input:
        return self.add_input(content, PromptStack.Role.USER_ROLE)

    def add_assistant_input(self, content: str) -> Input:
        return self.add_input(content, PromptStack.Role.ASSISTANT_ROLE)

    def add_tool_input(self, content: str) -> Input:
        return self.add_input(content, PromptStack.Role.TOOL_ROLE)

    def add_tool(self, tool: BaseTool) -> BaseTool:
        self.tools.append(tool)

        return self.tools[-1]

    def add_conversation_memory(self, memory: BaseConversationMemory, index: Optional[int] = None) -> list[Input]:
        """Add the Conversation Memory runs to the Prompt Stack.

        If autoprune is enabled, this will fit as many Conversation Memory runs into the Prompt Stack
        as possible without exceeding the token limit.

        Args:
            memory: The Conversation Memory to add the Prompt Stack to.
            index: Optional index to insert the Conversation Memory runs at.
                   Defaults to appending to the end of the Prompt Stack.
        """
        num_runs_to_fit_in_prompt = len(memory.runs)

        if memory.autoprune and hasattr(memory, "structure"):
            should_prune = True
            prompt_driver = memory.structure.config.prompt_driver
            temp_stack = PromptStack()

            # Try to determine how many Conversation Memory runs we can
            # fit into the Prompt Stack without exceeding the token limit.
            while should_prune and num_runs_to_fit_in_prompt > 0:
                temp_stack.inputs = self.inputs.copy()

                # Add n runs from Conversation Memory.
                # Where we insert into the Prompt Stack doesn't matter here
                # since we only care about the total token count.
                memory_inputs = memory.to_prompt_stack(num_runs_to_fit_in_prompt).inputs
                temp_stack.inputs.extend(memory_inputs)

                # Convert the prompt stack into tokens left.
                prompt_string = prompt_driver.prompt_stack_to_string(temp_stack)
                tokens_left = prompt_driver.tokenizer.count_input_tokens_left(prompt_string)
                if tokens_left > 0:
                    # There are still tokens left, no need to prune.
                    should_prune = False
                else:
                    # There were not any tokens left, prune one run and try again.
                    num_runs_to_fit_in_prompt -= 1

        if num_runs_to_fit_in_prompt:
            memory_inputs = memory.to_prompt_stack(num_runs_to_fit_in_prompt).inputs
            if index:
                self.inputs[index:index] = memory_inputs
            else:
                self.inputs.extend(memory_inputs)
        return self.inputs
