from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from marshmallow import Schema
from marshmallow import class_registry
from attr import define, field
from griptape.memory.structure import Run
from griptape.utils import PromptStack
from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from griptape.drivers import BaseConversationMemoryDriver
    from griptape.structures import Structure


@define
class BaseConversationMemory(SerializableMixin, ABC):
    driver: Optional[BaseConversationMemoryDriver] = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True, metadata={"serializable": True})
    structure: Structure = field(init=False)
    autoload: bool = field(default=True, kw_only=True)
    autoprune: bool = field(default=True, kw_only=True)
    max_runs: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        if self.driver and self.autoload:
            memory = self.driver.load()
            if memory is not None:
                [self.add_run(r) for r in memory.runs]

    def before_add_run(self) -> None:
        pass

    def add_run(self, run: Run) -> BaseConversationMemory:
        self.before_add_run()
        self.try_add_run(run)
        self.after_add_run()

        return self

    def after_add_run(self) -> None:
        if self.driver:
            self.driver.store(self)

    @abstractmethod
    def try_add_run(self, run: Run) -> None:
        ...

    @abstractmethod
    def to_prompt_stack(self, last_n: Optional[int] = None) -> PromptStack:
        ...

    @classmethod
    def try_get_schema(cls, obj_type: str) -> list[type[Schema]] | type[Schema]:
        from griptape.memory.structure import ConversationMemory, SummaryConversationMemory

        class_registry.register("ConversationMemory", BaseSchema.from_attrs_cls(ConversationMemory))
        class_registry.register("SummaryConversationMemory", BaseSchema.from_attrs_cls(SummaryConversationMemory))

        return class_registry.get_class(obj_type)
