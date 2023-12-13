from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError
from attr import define, field, Factory
from griptape.memory.structure import Run
from griptape.utils import PromptStack

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver
    from griptape.structures import Structure


@define
class ConversationMemory:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    driver: BaseConversationMemoryDriver | None = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True)
    structure: Structure = field(init=False)
    autoload: bool = field(default=True, kw_only=True)
    autoprune: bool = field(default=True, kw_only=True)
    max_runs: int | None = field(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.driver and self.autoload:
            memory = self.driver.load()
            if memory is not None:
                [self.add_run(r) for r in memory.runs]

    def add_run(self, run: Run) -> ConversationMemory:
        self.before_add_run()
        self.try_add_run(run)
        self.after_add_run()

        return self

    def before_add_run(self) -> None:
        pass

    def try_add_run(self, run: Run) -> None:
        self.runs.append(run)

        if self.max_runs:
            while len(self.runs) > self.max_runs:
                self.runs.pop(0)

    def after_add_run(self) -> None:
        if self.driver:
            self.driver.store(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        from griptape.schemas import ConversationMemorySchema

        return dict(ConversationMemorySchema().dump(self))

    def to_prompt_stack(self, last_n: int | None = None) -> PromptStack:
        prompt_stack = PromptStack()
        runs = self.runs[-last_n:] if last_n else self.runs
        for run in runs:
            prompt_stack.add_user_input(run.input)
            prompt_stack.add_assistant_input(run.output)
        return prompt_stack

    @classmethod
    def from_dict(cls, memory_dict: dict) -> ConversationMemory:
        from griptape.schemas import ConversationMemorySchema, SummaryConversationMemorySchema

        class_registry.register("ConversationMemory", ConversationMemorySchema)
        class_registry.register("SummaryConversationMemory", SummaryConversationMemorySchema)

        try:
            return class_registry.get_class(memory_dict["type"])().load(memory_dict)
        except RegistryError:
            raise ValueError("Unsupported memory type")

    @classmethod
    def from_json(cls, memory_json: str) -> ConversationMemory:
        return ConversationMemory.from_dict(json.loads(memory_json))
