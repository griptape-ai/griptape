from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field
from .prompt_stack import PromptStack

if TYPE_CHECKING:
    from griptape.memory.structure import ConversationMemory


@define(frozen=True)
class Conversation:
    memory: ConversationMemory = field()

    def lines(self) -> list[str]:
        lines = []

        for run in self.memory.runs:
            lines.append(f"Q: {run.input}")
            lines.append(f"A: {run.output}")

        return lines

    def prompt_stack(self, last_n: int) -> PromptStack:
        prompt_stack = PromptStack()
        for run in self.memory.runs[-last_n:]:
            prompt_stack.add_user_input(run.input)
            prompt_stack.add_assistant_input(run.output)
        return prompt_stack

    def __str__(self) -> str:
        return str.join("\n", self.lines())
