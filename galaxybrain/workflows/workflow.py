from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.rules import Rule
from galaxybrain.workflows import Memory

if TYPE_CHECKING:
    from galaxybrain.drivers import Driver
    from galaxybrain.workflows import Step


@define
class Workflow:
    driver: Driver = field(kw_only=True)
    root_step: Optional[Step] = field(default=None)
    rules: list[Rule] = field(default=[], kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)

    def __attrs_post_init__(self):
        if self.root_step:
            self.root_step.workflow = self

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
        return self.__last_step_after(self.root_step)

    def add_step(self, step: Step) -> Step:
        step.workflow = self

        if self.root_step is None:
            self.root_step = step
        else:
            self.last_step().add_child(step)

        return step

    def add_step_after(self, step: Step, new_step: Step) -> Step:
        new_step.workflow = self

        if step.child:
            new_step.add_child(step.child)
        step.add_child(new_step)

        return new_step

    def start(self) -> None:
        self.__run_from_step(self.root_step)

    def resume(self) -> None:
        self.__run_from_step(self.__next_unfinished_step(self.root_step))

    def to_string(self) -> Optional[str]:
        step = self.__last_finished_step(self.root_step)

        if step is None:
            return None
        else:
            return step.to_string()

    def __last_step_after(self, step: Optional[Step]) -> Optional[Step]:
        if step is None:
            return None
        elif step.child:
            return self.__last_step_after(step.child)
        else:
            return step

    def __run_from_step(self, step: Optional[Step]) -> None:
        if step is None:
            return
        else:
            step.run()

            self.memory.add_step(self, step)

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
