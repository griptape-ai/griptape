from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.memory.structure import Run

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver
    from griptape.structures import Structure
    from griptape.utils import PromptStack


@define
class ConversationMemory:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    driver: Optional[BaseConversationMemoryDriver] = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True)
    structure: Structure = field(init=False)
    autoload: bool = field(default=True, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.driver and self.autoload:
            memory = self.driver.load()
            if memory is not None:
                [self.add_run(r) for r in memory.runs]

    def add_to_prompt_stack(self, stack: PromptStack) -> None:
        for r in self.runs:
            stack.add_user_input(r.input)
            stack.add_assistant_input(r.output)

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
