from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.events import StartTaskEvent, FinishTaskEvent
from griptape.artifacts import ErrorArtifact

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.tasks import BaseTask
    from griptape.structures import Structure


@define
class BaseTask(ABC):
    class State(Enum):
        PENDING = 1
        EXECUTING = 2
        FINISHED = 3

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    state: State = field(default=State.PENDING, kw_only=True)
    parent_ids: list[str] = field(factory=list, kw_only=True)
    child_ids: list[str] = field(factory=list, kw_only=True)

    output: Optional[BaseArtifact] = field(default=None, init=False)
    structure: Optional[Structure] = field(default=None, init=False)

    @property
    @abstractmethod
    def input(self) -> BaseArtifact:
        ...

    @property
    def parents(self) -> list[BaseTask]:
        return [self.structure.find_task(parent_id) for parent_id in self.parent_ids]

    @property
    def children(self) -> list[BaseTask]:
        return [self.structure.find_task(child_id) for child_id in self.child_ids]

    def __rshift__(self, child: BaseTask) -> BaseTask:
        return self.add_child(child)

    def __lshift__(self, child: BaseTask) -> BaseTask:
        return self.add_parent(child)

    def preprocess(self, structure: Structure) -> BaseTask:
        self.structure = structure

        return self

    def add_child(self, child: BaseTask) -> BaseTask:
        if self.structure:
            child.structure = self.structure
        elif child.structure:
            self.structure = child.structure

        if child not in self.structure.tasks:
            self.structure.tasks.append(child)

        if self not in self.structure.tasks:
            self.structure.tasks.append(self)

        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        return child

    def add_parent(self, parent: BaseTask) -> BaseTask:
        if self.structure:
            parent.structure = self.structure
        elif parent.structure:
            self.structure = parent.structure

        if parent not in self.structure.tasks:
            self.structure.tasks.append(parent)

        if self not in self.structure.tasks:
            self.structure.tasks.append(self)

        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        return parent

    def is_pending(self) -> bool:
        return self.state == BaseTask.State.PENDING

    def is_finished(self) -> bool:
        return self.state == BaseTask.State.FINISHED

    def is_executing(self) -> bool:
        return self.state == BaseTask.State.EXECUTING

    def before_run(self) -> None:
        pass

    def after_run(self) -> None:
        pass

    def execute(self) -> BaseArtifact:
        try:
            self.state = BaseTask.State.EXECUTING

            self.structure.publish_event(StartTaskEvent(task=self))
            self.before_run()

            self.output = self.run()

            self.after_run()
        except Exception as e:
            self.structure.logger.error(f"{self.__class__.__name__} {self.id}\n{e}", exc_info=True)

            self.output = ErrorArtifact(str(e))
        finally:
            self.state = BaseTask.State.FINISHED
            self.structure.publish_event(FinishTaskEvent(task=self))

            return self.output

    def can_execute(self) -> bool:
        return self.state == BaseTask.State.PENDING and all(parent.is_finished() for parent in self.parents)

    def reset(self) -> BaseTask:
        self.state = BaseTask.State.PENDING
        self.output = None

        return self

    @abstractmethod
    def run(self) -> BaseArtifact:
        ...
