from abc import ABC
from typing import Optional
from attr import define, field
from griptape.memory import Memory
from griptape.structures import Structure


@define
class StructureWithMemory(Structure, ABC):
    memory: Optional[Memory] = field(default=None, kw_only=True)
    autoprune_memory: bool = field(default=True, kw_only=True)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.memory:
            self.memory.structure = self

    def add_memory_to_prompt_stack(self, stack: list[str], task_prompt: str) -> list[str]:
        if self.memory:
            if self.autoprune_memory:
                last_n = len(self.memory.runs)
                should_prune = True

                while should_prune and last_n > 0:
                    temp_stack = stack.copy()
                    temp_stack.append(task_prompt)

                    temp_stack.append(self.memory.to_prompt_string(last_n))

                    if self.prompt_driver.tokenizer.tokens_left(self.stack_to_prompt_string(temp_stack)) > 0:
                        should_prune = False
                    else:
                        last_n -= 1

                if last_n > 0:
                    stack.append(self.memory.to_prompt_string(last_n))
            else:
                stack.append(self.memory.to_prompt_string())

        stack.append(task_prompt)

        return stack
