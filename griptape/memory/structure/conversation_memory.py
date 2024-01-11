from __future__ import annotations
from typing import TYPE_CHECKING
from marshmallow import Schema
from marshmallow import class_registry
from attr import define, field
from griptape.memory.structure import Run
from griptape.utils import PromptStack
from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver
    from griptape.structures import Structure


@define
class ConversationMemory(SerializableMixin):
    driver: BaseConversationMemoryDriver | None = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True, metadata={"serialize": True})
    structure: Structure = field(init=False)
    autoload: bool = field(default=True, kw_only=True)
    autoprune: bool = field(default=True, kw_only=True)
    max_runs: int | None = field(default=None, kw_only=True, metadata={"serialize": True})

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

    def to_prompt_stack(self, last_n: int | None = None) -> PromptStack:
        prompt_stack = PromptStack()
        runs = self.runs[-last_n:] if last_n else self.runs
        for run in runs:
            prompt_stack.add_user_input(run.input)
            prompt_stack.add_assistant_input(run.output)
        return prompt_stack

    @classmethod
    def try_get_schema(cls, obj_type: str) -> list[type[Schema]] | type[Schema]:
        from griptape.memory.structure import ConversationMemory, SummaryConversationMemory

        class_registry.register("ConversationMemory", BaseSchema.from_attrscls(ConversationMemory))
        class_registry.register("SummaryConversationMemory", BaseSchema.from_attrscls(SummaryConversationMemory))

        return class_registry.get_class(obj_type)
