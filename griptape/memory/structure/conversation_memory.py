from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.memory.structure import Run
from griptape.utils import PromptStack
from griptape.utils import Conversation

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver
    from griptape.structures import Structure


@define
class ConversationMemory:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    driver: Optional[BaseConversationMemoryDriver] = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True)
    structure: Structure = field(init=False)
    autoload: bool = field(default=True, kw_only=True)
    autoprune: bool = field(default=True, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.driver and self.autoload:
            memory = self.driver.load()
            if memory is not None:
                [self.add_run(r) for r in memory.runs]

    def add_to_prompt_stack(self, stack: PromptStack, index: Optional[int]=None) -> None:
        """Add the Conversation Memory runs to the Prompt Stack.

        If autoprune is enabled, this will fit as many Conversation Memory runs into the Prompt Stack
        as possible without exceeding the token limit.

        Args:
            stack: The Prompt Stack to add the Conversation Memory runs to.
            index: Optional index to insert the Monversation Memory runs at.
                   Defaults to appending to the end of the Prompt Stack.
        """
        runs_to_fit_in_prompt = len(self.runs)

        if self.autoprune and hasattr(self, "structure"):
            should_prune = True
            prompt_driver = self.structure.prompt_driver
            temp_stack = PromptStack()

            # Try to determine how many Conversation Memory runs we can 
            # fit into the Prompt Stack without exceeding the token limit.
            while should_prune and runs_to_fit_in_prompt > 0:
                temp_stack.inputs = stack.inputs.copy()

                # Add n runs from Conversation Memory.
                # Where we insert into the Prompt Stack doesn't matter here
                # since we only care about the total token count.
                memory_inputs = Conversation(self).prompt_stack(runs_to_fit_in_prompt).inputs
                temp_stack.inputs.extend(memory_inputs)

                # Convert the prompt stack into tokens left.
                prompt_string = prompt_driver.prompt_stack_to_string(temp_stack)
                tokens_left = prompt_driver.tokenizer.tokens_left(prompt_string)
                if tokens_left > 0:
                    # There are still tokens left, no need to prune.
                    should_prune = False
                else:
                    # There were not any tokens left, prune one run and try again.
                    runs_to_fit_in_prompt -= 1

        if runs_to_fit_in_prompt:
            memory_inputs = Conversation(self).prompt_stack(runs_to_fit_in_prompt).inputs
            if index:
                stack.inputs[index:index] = memory_inputs
            else:
                stack.inputs.extend(memory_inputs)
            

    def add_run(self, run: Run) -> ConversationMemory:
        self.before_add_run()
        self.try_add_run(run)
        self.after_add_run()

        return self

    def before_add_run(self) -> None:
        pass

    def try_add_run(self, run: Run) -> None:
        self.runs.append(run)

    def after_add_run(self) -> None:
        if self.driver:
            self.driver.store(self)

    def is_empty(self) -> bool:
        return not self.runs

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        from griptape.schemas import ConversationMemorySchema

        return dict(ConversationMemorySchema().dump(self))

    @classmethod
    def from_dict(cls, memory_dict: dict) -> ConversationMemory:
        from griptape.schemas import ConversationMemorySchema

        return ConversationMemorySchema().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> ConversationMemory:
        return ConversationMemory.from_dict(json.loads(memory_json))
