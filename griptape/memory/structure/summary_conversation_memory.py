from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING
from typing import Optional
from attr import define, field, Factory
from griptape.drivers import OpenAiChatPromptDriver
from griptape.schemas import SummaryConversationMemorySchema
from griptape.utils import J2, PromptStack
from griptape.memory.structure import ConversationMemory
from griptape.tokenizers import OpenAiTokenizer

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.memory.structure import Run


@define
class SummaryConversationMemory(ConversationMemory):
    offset: int = field(default=1, kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    summary: str | None = field(default=None, kw_only=True)
    summary_index: int = field(default=0, kw_only=True)
    summary_template_generator: J2 = field(default=Factory(lambda: J2("memory/conversation/summary.j2")), kw_only=True)
    summarize_conversation_template_generator: J2 = field(
        default=Factory(lambda: J2("memory/conversation/summarize_conversation.j2")), kw_only=True
    )

    @classmethod
    def from_dict(cls, memory_dict: dict) -> SummaryConversationMemory:
        return SummaryConversationMemorySchema().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> SummaryConversationMemory:
        return SummaryConversationMemory.from_dict(json.loads(memory_json))

    def to_prompt_stack(self, last_n: int | None = None) -> PromptStack:
        stack = PromptStack()
        if self.summary:
            stack.add_user_input(self.summary_template_generator.render(summary=self.summary))

        for r in self.unsummarized_runs(last_n):
            stack.add_user_input(r.input)
            stack.add_assistant_input(r.output)

        return stack

    def to_dict(self) -> dict:
        return dict(SummaryConversationMemorySchema().dump(self))

    def unsummarized_runs(self, last_n: int | None = None) -> list[Run]:
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

    def summarize_runs(self, previous_summary: str, runs: list[Run]) -> str:
        try:
            if len(runs) > 0:
                summary = self.summarize_conversation_template_generator.render(summary=previous_summary, runs=runs)
                return self.prompt_driver.run(
                    prompt_stack=PromptStack(inputs=[PromptStack.Input(summary, role=PromptStack.USER_ROLE)])
                ).to_text()
            else:
                return previous_summary
        except Exception as e:
            logging.error(f"Error summarizing memory: {type(e).__name__}({e})")

            return previous_summary
