from __future__ import annotations
from attrs import define
from typing import Optional
from griptape.memory.structure import Run, BaseConversationMemory
from griptape.common import MessageStack


@define
class ConversationMemory(BaseConversationMemory):
    def try_add_run(self, run: Run) -> None:
        self.runs.append(run)

        if self.max_runs:
            while len(self.runs) > self.max_runs:
                self.runs.pop(0)

    def to_message_stack(self, last_n: Optional[int] = None) -> MessageStack:
        message_stack = MessageStack()
        runs = self.runs[-last_n:] if last_n else self.runs
        for run in runs:
            message_stack.add_user_message(run.input)
            message_stack.add_assistant_message(run.output)
        return message_stack
