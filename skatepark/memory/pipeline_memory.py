from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from skatepark.memory import PipelineRun
from skatepark.utils import J2

if TYPE_CHECKING:
    from skatepark.drivers import MemoryDriver
    from skatepark.structures import Pipeline


@define
class PipelineMemory:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    driver: Optional[MemoryDriver] = field(default=None, kw_only=True)
    runs: list[PipelineRun] = field(factory=list, kw_only=True)
    pipeline: Pipeline = field(init=False)

    def add_run(self, run: PipelineRun) -> PipelineMemory:
        self.before_add_run()
        self.process_add_run(run)
        self.after_add_run()

        return self

    def before_add_run(self) -> None:
        pass

    def process_add_run(self, run: PipelineRun) -> None:
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
        from skatepark.schemas import PipelineMemorySchema

        return PipelineMemorySchema().dump(self)

    @classmethod
    def from_dict(cls, memory_dict: dict) -> PipelineMemory:
        from skatepark.schemas import PipelineMemorySchema

        return PipelineMemorySchema().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> PipelineMemory:
        return PipelineMemory.from_dict(json.loads(memory_json))
