from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.common import PromptStack
from griptape.configs import Defaults
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils import dict_merge

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver, BasePromptDriver
    from griptape.memory.structure import Run


@define
class BaseConversationMemory(SerializableMixin, ABC):
    conversation_memory_driver: BaseConversationMemoryDriver = field(
        default=Factory(lambda: Defaults.drivers_config.conversation_memory_driver), kw_only=True
    )
    runs: list[Run] = field(factory=list, kw_only=True, metadata={"serializable": True})
    meta: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    autoload: bool = field(default=True, kw_only=True)
    autoprune: bool = field(default=True, kw_only=True)
    max_runs: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        if self.autoload:
            self.load_runs()

    def before_add_run(self) -> None:
        pass

    def add_run(self, run: Run) -> BaseConversationMemory:
        self.before_add_run()
        self.try_add_run(run)
        self.after_add_run()

        return self

    def after_add_run(self) -> None:
        if self.max_runs:
            while len(self.runs) > self.max_runs:
                self.runs.pop(0)
        self.conversation_memory_driver.store(self.runs, self.meta)

    @abstractmethod
    def try_add_run(self, run: Run) -> None: ...

    @abstractmethod
    def to_prompt_stack(self, last_n: Optional[int] = None) -> PromptStack: ...

    def load_runs(self) -> list[Run]:
        runs, meta = self.conversation_memory_driver.load()
        self.runs.extend(runs)
        self.meta = dict_merge(self.meta, meta)

        return self.runs

    def add_to_prompt_stack(
        self, prompt_driver: BasePromptDriver, prompt_stack: PromptStack, index: Optional[int] = None
    ) -> PromptStack:
        """Add the Conversation Memory runs to the Prompt Stack by modifying the messages in place.

        If autoprune is enabled, this will fit as many Conversation Memory runs into the Prompt Stack
        as possible without exceeding the token limit.

        Args:
            prompt_driver: The Prompt Driver to use for token counting.
            prompt_stack: The Prompt Stack to add the Conversation Memory to.
            index: Optional index to insert the Conversation Memory runs at.
                   Defaults to appending to the end of the Prompt Stack.
        """
        num_runs_to_fit_in_prompt = len(self.runs)

        if self.autoprune:
            should_prune = True
            temp_stack = PromptStack()

            # Try to determine how many Conversation Memory runs we can
            # fit into the Prompt Stack without exceeding the token limit.
            while should_prune and num_runs_to_fit_in_prompt > 0:
                temp_stack.messages = prompt_stack.messages.copy()

                # Add n runs from Conversation Memory.
                # Where we insert into the Prompt Stack doesn't matter here
                # since we only care about the total token count.
                memory_inputs = self.to_prompt_stack(num_runs_to_fit_in_prompt).messages
                temp_stack.messages.extend(memory_inputs)

                # Convert the Prompt Stack into tokens left.
                tokens_left = prompt_driver.tokenizer.count_input_tokens_left(
                    prompt_driver.prompt_stack_to_string(temp_stack),
                )
                if tokens_left > 0:
                    # There are still tokens left, no need to prune.
                    should_prune = False
                else:
                    # There were not any tokens left, prune one run and try again.
                    num_runs_to_fit_in_prompt -= 1

        if num_runs_to_fit_in_prompt:
            memory_inputs = self.to_prompt_stack(num_runs_to_fit_in_prompt).messages
            if index is None:
                prompt_stack.messages.extend(memory_inputs)
            else:
                prompt_stack.messages[index:index] = memory_inputs

        return prompt_stack
