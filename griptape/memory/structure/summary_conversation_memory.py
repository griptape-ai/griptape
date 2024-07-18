from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.common import PromptStack
from griptape.common.prompt_stack.messages.message import Message
from griptape.memory.structure import ConversationMemory
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.memory.structure import Run


@define
class SummaryConversationMemory(ConversationMemory):
    offset: int = field(default=1, kw_only=True, metadata={"serializable": True})
    _prompt_driver: BasePromptDriver = field(kw_only=True, default=None, alias="prompt_driver")
    summary: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    summary_index: int = field(default=0, kw_only=True, metadata={"serializable": True})
    summary_template_generator: J2 = field(default=Factory(lambda: J2("memory/conversation/summary.j2")), kw_only=True)
    summarize_conversation_template_generator: J2 = field(
        default=Factory(lambda: J2("memory/conversation/summarize_conversation.j2")),
        kw_only=True,
    )

    @property
    def prompt_driver(self) -> BasePromptDriver:
        if self._prompt_driver is None:
            if self.structure is not None:
                self._prompt_driver = self.structure.config.prompt_driver
            else:
                raise ValueError("Prompt Driver is not set.")
        return self._prompt_driver

    @prompt_driver.setter
    def prompt_driver(self, value: BasePromptDriver) -> None:
        self._prompt_driver = value

    def to_prompt_stack(self, last_n: Optional[int] = None) -> PromptStack:
        stack = PromptStack()
        if self.summary:
            stack.add_user_message(self.summary_template_generator.render(summary=self.summary))

        for r in self.unsummarized_runs(last_n):
            stack.add_user_message(r.input)
            stack.add_assistant_message(r.output)

        return stack

    def unsummarized_runs(self, last_n: Optional[int] = None) -> list[Run]:
        summary_index_runs = self.runs[self.summary_index :]

        if last_n:
            last_n_runs = self.runs[-last_n:]

            if len(summary_index_runs) > len(last_n_runs):
                return last_n_runs
            else:
                return summary_index_runs
        else:
            return summary_index_runs

    def try_add_run(self, run: Run) -> None:
        super().try_add_run(run)

        unsummarized_runs = self.unsummarized_runs()
        runs_to_summarize = unsummarized_runs[: max(0, len(unsummarized_runs) - self.offset)]

        if len(runs_to_summarize) > 0:
            self.summary = self.summarize_runs(self.summary, runs_to_summarize)
            self.summary_index = 1 + self.runs.index(runs_to_summarize[-1])

    def summarize_runs(self, previous_summary: str | None, runs: list[Run]) -> str | None:
        try:
            if len(runs) > 0:
                summary = self.summarize_conversation_template_generator.render(summary=previous_summary, runs=runs)
                return self.prompt_driver.run(
                    prompt_stack=PromptStack(messages=[Message(summary, role=Message.USER_ROLE)]),
                ).to_text()
            else:
                return previous_summary
        except Exception as e:
            logging.exception("Error summarizing memory: %s(%s)", type(e).__name__, e)

            return previous_summary
