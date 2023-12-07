from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from attr import define, field

if TYPE_CHECKING:
    from griptape.memory.structure import ConversationMemory


@define
class PromptStack:
    GENERIC_ROLE = "generic"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    @dataclass
    class Input:
        content: str | list[dict]
        role: str

        def is_generic(self) -> bool:
            return self.role == PromptStack.GENERIC_ROLE

        def is_system(self) -> bool:
            return self.role == PromptStack.SYSTEM_ROLE

        def is_user(self) -> bool:
            return self.role == PromptStack.USER_ROLE

        def is_assistant(self) -> bool:
            return self.role == PromptStack.ASSISTANT_ROLE

    inputs: list[Input] = field(factory=list, kw_only=True)

    def add_input(self, content: str, role: str) -> Input:
        self.inputs.append(self.Input(content=content, role=role))

        return self.inputs[-1]

    def add_generic_input(self, content: str) -> Input:
        return self.add_input(content, self.GENERIC_ROLE)

    def add_system_input(self, content: str) -> Input:
        return self.add_input(content, self.SYSTEM_ROLE)

    def add_user_input(self, content: str) -> Input:
        return self.add_input(content, self.USER_ROLE)

    def add_assistant_input(self, content: str) -> Input:
        return self.add_input(content, self.ASSISTANT_ROLE)

    def add_conversation_memory(self, memory: ConversationMemory, index: int | None = None) -> list[Input]:
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
            prompt_driver = memory.structure.prompt_driver
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
                tokens_left = prompt_driver.tokenizer.count_tokens_left(prompt_string)
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
