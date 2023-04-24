from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.memory import Run
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import MemoryDriver
    from griptape.structures import Structure


@define
class Memory:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    driver: Optional[MemoryDriver] = field(default=None, kw_only=True)
    runs: list[Run] = field(factory=list, kw_only=True)
    structure: Structure = field(init=False)

    def add_run(self, run: Run) -> Memory:
        self.before_add_run()
        self.process_add_run(run)
        self.after_add_run()

        return self

    def before_add_run(self) -> None:
        pass

    def process_add_run(self, run: Run) -> None:
        self.runs.append(run)

    def after_add_run(self) -> None:
        if self.driver:
            self.driver.store(self)

    def is_empty(self) -> bool:
        return not self.runs

    def to_prompt_string(self, last_n: Optional[int] = None) -> str:
        return J2("prompts/memory.j2").render(
            runs=self.runs if last_n is None else self.runs[-last_n:]
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        from griptape.schemas import MemorySchema

        return MemorySchema().dump(self)

    @classmethod
    def from_dict(cls, memory_dict: dict) -> Memory:
        from griptape.schemas import MemorySchema

        return MemorySchema().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> Memory:
        return Memory.from_dict(json.loads(memory_json))
