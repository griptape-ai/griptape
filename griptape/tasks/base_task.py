from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field, fields

from griptape.artifacts import ErrorArtifact
from griptape.configs import Defaults
from griptape.events import EventBus, FinishTaskEvent, StartTaskEvent
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.memory.meta import BaseMetaEntry
    from griptape.structures import Structure

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseTask(FuturesExecutorMixin, SerializableMixin, ABC):
    class State(Enum):
        PENDING = 1
        EXECUTING = 2
        FINISHED = 3

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    state: State = field(default=State.PENDING, kw_only=True, metadata={"serializable": True})
    parent_ids: list[str] = field(factory=list, kw_only=True, metadata={"serializable": True})
    child_ids: list[str] = field(factory=list, kw_only=True, metadata={"serializable": True})
    max_meta_memory_entries: Optional[int] = field(default=20, kw_only=True)
    structure: Optional[Structure] = field(default=None, kw_only=True, metadata={"serializable": True})

    output: Optional[BaseArtifact] = field(default=None, init=False, metadata={"serializable": True})
    context: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})

    def __rshift__(self, other: BaseTask) -> BaseTask:
        self.add_child(other)

        return other

    def __lshift__(self, other: BaseTask) -> BaseTask:
        self.add_parent(other)

        return other

    def __attrs_post_init__(self) -> None:
        if self.structure is not None:
            self.structure.add_task(self)

    @property
    @abstractmethod
    def input(self) -> BaseArtifact: ...

    @property
    def parents(self) -> list[BaseTask]:
        if self.structure is not None:
            return [self.structure.find_task(parent_id) for parent_id in self.parent_ids]
        raise ValueError("Structure must be set to access parents")

    @property
    def children(self) -> list[BaseTask]:
        if self.structure is not None:
            return [self.structure.find_task(child_id) for child_id in self.child_ids]
        raise ValueError("Structure must be set to access children")

    @property
    def parent_outputs(self) -> dict[str, str]:
        return {parent.id: parent.output.to_text() if parent.output else "" for parent in self.parents}

    @property
    def parents_output_text(self) -> str:
        return "\n".join([parent.output.to_text() for parent in self.parents if parent.output])

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

    def add_parents(self, parents: list[BaseTask]) -> None:
        for parent in parents:
            self.add_parent(parent)

    def add_parent(self, parent: BaseTask) -> BaseTask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        if self.structure is not None:
            self.structure.add_task(parent)

        return self

    def add_children(self, children: list[BaseTask]) -> None:
        for child in children:
            self.add_child(child)

    def add_child(self, child: BaseTask) -> BaseTask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        if self.structure is not None:
            self.structure.add_task(child)

        return self

    def preprocess(self, structure: Structure) -> BaseTask:
        self.structure = structure

        return self

    def is_pending(self) -> bool:
        return self.state == BaseTask.State.PENDING

    def is_finished(self) -> bool:
        return self.state == BaseTask.State.FINISHED

    def is_executing(self) -> bool:
        return self.state == BaseTask.State.EXECUTING

    def before_run(self) -> None:
        if self.structure is not None:
            EventBus.publish_event(
                StartTaskEvent(
                    task_id=self.id,
                    task_parent_ids=self.parent_ids,
                    task_child_ids=self.child_ids,
                    task_input=self.input,
                    task_output=self.output,
                ),
            )

    def after_run(self) -> None:
        if self.structure is not None:
            EventBus.publish_event(
                FinishTaskEvent(
                    task_id=self.id,
                    task_parent_ids=self.parent_ids,
                    task_child_ids=self.child_ids,
                    task_input=self.input,
                    task_output=self.output,
                ),
            )

    def execute(self) -> Optional[BaseArtifact]:
        try:
            self.state = BaseTask.State.EXECUTING

            self.before_run()

            self.output = self.run()

            self.after_run()
        except Exception as e:
            logger.exception("%s %s\n%s", self.__class__.__name__, self.id, e)

            self.output = ErrorArtifact(str(e), exception=e)
        finally:
            self.state = BaseTask.State.FINISHED

        return self.output

    def can_execute(self) -> bool:
        return self.state == BaseTask.State.PENDING and all(parent.is_finished() for parent in self.parents)

    def reset(self) -> BaseTask:
        self.state = BaseTask.State.PENDING
        self.output = None

        return self

    @abstractmethod
    def run(self) -> BaseArtifact: ...

    @property
    def full_context(self) -> dict[str, Any]:
        if self.structure:
            structure_context = self.structure.context(self)

            structure_context.update(self.context)

            return structure_context
        else:
            return {}

    def to_dict(self) -> dict:
        """Converts attributes with metadata={"serializable": True} into a dictionary."""
        serialized_data = {}

        # Use the attrs library to access fields with metadata.
        for _field in fields(self.__class__):
            if _field.metadata.get("serializable", False):
                value = getattr(self, _field.name)
                serialized_data[_field.name] = self._serialize(value)

        return serialized_data

    def _serialize(self, value: Any) -> Any:
        if hasattr(value, "to_dict"):  # Check if the object has a to_dict method
            return value.to_dict()
        elif isinstance(value, (list, tuple)):  # Handle lists or tuples
            return [self._serialize(item) for item in value]
        elif isinstance(value, dict):  # Handle dictionaries
            return {key: self._serialize(val) for key, val in value.items()}
        elif isinstance(value, Enum):  # Handle Enum types
            return value.name  # Return the Enum's name as a string
        elif callable(value):  # Handle functions or methods
            return "default_function"
        else:
            return repr(value)  # Fallback for other non-serializable objects
