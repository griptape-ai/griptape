from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Attribute, define, field

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


@define(frozen=True)
class Conversation:
    memory: BaseConversationMemory | None = field()

    @memory.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_memory(self, attribute: Attribute, value: BaseConversationMemory | None) -> None:
        if value is None:
            raise ValueError("Conversation memory must not be None.")

    def lines(self) -> list[str]:
        from griptape.memory.structure import SummaryConversationMemory

        lines = []

        for run in self.memory.runs if self.memory is not None else []:
            lines.extend((f"Q: {run.input}", f"A: {run.output}"))

        if isinstance(self.memory, SummaryConversationMemory):
            lines.append(f"Summary: {self.memory.summary}")

        return lines

    def prompt_stack(self) -> list[str]:
        from griptape.memory.structure import SummaryConversationMemory

        lines = []

        for stack in self.memory.to_prompt_stack().messages if self.memory is not None else []:
            lines.append(f"{stack.role}: {stack.to_text()}")

        if isinstance(self.memory, SummaryConversationMemory):
            lines.append(f"Summary: {self.memory.summary}")

        return lines

    def __str__(self) -> str:
        return str.join("\n", self.lines())
