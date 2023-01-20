from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.rules import Rule
from galaxybrain.summarizers import Summarizer, DriverSummarizer
from galaxybrain.workflows import Memory

if TYPE_CHECKING:
    from galaxybrain.drivers import Driver
    from galaxybrain.workflows import Step


@define
class Workflow:
    root_step: Optional[Step] = field(default=None)
    driver: Driver = field(kw_only=True)
    rules: list[Rule] = field(default=[], kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)
    summarizer: Summarizer = field(default=DriverSummarizer(), kw_only=True)

    def steps(self):
        all_steps = []
        current_step = self.root_step

        if current_step:
            all_steps.append(current_step)

            while current_step.child is not None:
                current_step = current_step.child

                all_steps.append(current_step)

        return all_steps

    def last_step(self) -> Optional[Step]:
        return self.last_step_after(self.root_step)

    def last_step_after(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.child:
            return self.last_step_after(step.child)
        else:
            return step

    def add_step(self, step: Step) -> Step:
        if self.root_step is None:
            self.root_step = step
        else:
            self.last_step().add_child(step)

        return step

    def start(self) -> None:
        self.__run_from_step(self.root_step)

    def resume(self) -> None:
        self.__run_from_step(self.__next_unfinished_step(self.root_step))

    def to_string(self) -> Optional[str]:
        step = self.__last_finished_step(self.root_step)

        if step is None:
            return None
        else:
            return step.to_string(rules=self.rules, memory=self.memory)

    def __run_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            step.run(workflow=self)

            self.memory.add_step(step)

            if self.memory.should_summarize:
                self.memory.summary = self.summarizer.summarize(self, step)

            self.__run_from_step(step.child)

    def __next_unfinished_step(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.is_finished():
            return self.__next_unfinished_step(step.child)
        else:
            return step

    def __last_finished_step(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.is_finished():
            if step.child:
                if step.child.is_finished():
                    return self.__last_finished_step(step.child)
                else:
                    return step
            else:
                return step
        else:
            return None
