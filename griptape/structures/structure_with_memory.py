from abc import ABC
from typing import Optional
from attr import define, field
from griptape.memory.structure import ConversationMemory
from griptape.structures import Structure


@define
class StructureWithMemory(Structure, ABC):
    memory: Optional[ConversationMemory] = field(default=None, kw_only=True)
    autoprune_memory: bool = field(default=True, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.memory:
            self.memory.structure = self

        super().__attrs_post_init__()

    def add_memory_to_prompt_stack(self, system_prompt: str, task_prompt: str) -> list[str]:
        prompt_stack = [
            system_prompt
        ]

        if self.memory:
            if self.autoprune_memory:
                last_n = len(self.memory.runs)
                should_prune = True

                while should_prune and last_n > 0:
                    temp_prompt_stack = prompt_stack.copy()
                    temp_prompt_stack.append(task_prompt)

                    temp_prompt_stack.append(self.memory.to_prompt_string(last_n))

                    if self.prompt_driver.tokenizer.tokens_left(self.stack_to_prompt_string(temp_prompt_stack)) > 0:
                        should_prune = False
                    else:
                        last_n -= 1

                prompt_stack.append(self.memory.to_prompt_string(last_n))
            else:
                prompt_stack.append(self.memory.to_prompt_string())

        prompt_stack.append(task_prompt)

        return prompt_stack
