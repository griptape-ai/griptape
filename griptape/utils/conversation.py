from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from griptape.memory.structure import ConversationMemory


@define(frozen=True)
class Conversation:
    memory: ConversationMemory = field()

    def lines(self) -> list[str]:
        lines = []

        for run in self.memory.runs:
            lines.extend((f"Q: {run.input}", f"A: {run.output}"))

        return lines

    def prompt_stack(self) -> list[str]:
        lines = []

        for stack in self.memory.to_prompt_stack().messages:
            lines.append(f"{stack.role}: {stack.to_text()}")

        return lines

    def __str__(self) -> str:
        return str.join("\n", self.lines())
