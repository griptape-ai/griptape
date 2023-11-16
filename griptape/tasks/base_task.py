from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.events import StartTaskEvent, FinishTaskEvent
from griptape.artifacts import ErrorArtifact, TextArtifact, InfoArtifact, BaseArtifact

if TYPE_CHECKING:
    from griptape.structures import Structure
    from griptape.memory.meta import BaseMetaEntry
    from griptape.memory import TaskMemory


@define
class BaseTask(ABC):
    """Abstract class for all tasks to inherit from.

    Attributes:
        input_memory: TaskMemory available in tool activities. Gets automatically set if None.
        output_memory: TaskMemory that activities write to be default. Gets automatically set if None.
        off_prompt: Determines whether tool activity output goes to the output memory.
    """

    class State(Enum):
        PENDING = 1
        EXECUTING = 2
        FINISHED = 3

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    name: str = field(default=Factory(lambda self: self.class_name, takes_self=True), kw_only=True)
    state: State = field(default=State.PENDING, kw_only=True)
    parent_ids: list[str] = field(factory=list, kw_only=True)
    child_ids: list[str] = field(factory=list, kw_only=True)
    max_meta_memory_entries: Optional[int] = field(default=20, kw_only=True)
    off_prompt: bool = field(default=False, kw_only=True)
    task_memory: Optional[TaskMemory] = field(default=None, kw_only=True)

    output: Optional[BaseArtifact] = field(default=None, init=False)
    structure: Optional[Structure] = field(default=None, init=False)

    @property
    def class_name(self):
        return self.__class__.__name__

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

    @property
    def meta_memories(self) -> list[BaseMetaEntry]:
        if self.structure and self.structure.meta_memory:
            if self.max_meta_memory_entries:
                return self.structure.meta_memory.entries[: self.max_meta_memory_entries]
            else:
                return self.structure.meta_memory.entries
        else:
            return []

    def __str__(self) -> str:
        return str(self.output.value)

    def preprocess(self, structure: Structure) -> BaseTask:
        self.structure = structure

        print("PREPROCESS", self.__class__.__name__, self.task_memory is None, structure.task_memory is None)
        if self.task_memory is None and structure.task_memory:
            self.set_default_task_memory(structure.task_memory)

        return self

    def is_pending(self) -> bool:
        return self.state == BaseTask.State.PENDING

    def is_finished(self) -> bool:
        return self.state == BaseTask.State.FINISHED

    def is_executing(self) -> bool:
        return self.state == BaseTask.State.EXECUTING

    def before_run(self) -> None:
        if self.structure:
            self.structure.publish_event(StartTaskEvent.from_task(self))

    def after_run(self, output: BaseArtifact) -> BaseArtifact:
        if self.structure:
            self.structure.publish_event(FinishTaskEvent.from_task(self))

        print("AFTER RUN", self.__class__.__name__, self.off_prompt, self.task_memory is None)
        if output:
            if self.task_memory:
                processed_output = self.structure.task_memory.process_output(self, output)

                if isinstance(processed_output, BaseArtifact):
                    return processed_output
                else:
                    return TextArtifact(str(processed_output))
            else:
                return output
        else:
            return InfoArtifact("Tool returned an empty output")

    def execute(self) -> Optional[BaseArtifact]:
        try:
            self.state = BaseTask.State.EXECUTING

            self.before_run()

            output = self.run()

            self.output = self.after_run(output)
        except Exception as e:
            self.structure.logger.error(f"{self.__class__.__name__} {self.id}\n{e}", exc_info=True)

            self.output = ErrorArtifact(str(e))
        finally:
            self.state = BaseTask.State.FINISHED

            return self.output

    def can_execute(self) -> bool:
        return self.state == BaseTask.State.PENDING and all(parent.is_finished() for parent in self.parents)

    def reset(self) -> BaseTask:
        self.state = BaseTask.State.PENDING
        self.output = None

        return self

    def set_default_task_memory(self, memory: TaskMemory) -> None:
        self.task_memory = memory

    @abstractmethod
    def run(self) -> BaseArtifact:
        ...
