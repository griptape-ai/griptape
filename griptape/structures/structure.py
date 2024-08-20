from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from attrs import Attribute, Factory, define, field

from griptape.common import observable
from griptape.events import EventBus, FinishStructureRunEvent, StartStructureRunEvent
from griptape.memory import TaskMemory
from griptape.memory.meta import MetaMemory
from griptape.memory.structure import ConversationMemory

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.memory.structure import BaseConversationMemory
    from griptape.rules import Rule, Ruleset
    from griptape.tasks import BaseTask


@define
class Structure(ABC):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    conversation_memory: Optional[BaseConversationMemory] = field(
        default=Factory(lambda: ConversationMemory()),
        kw_only=True,
    )
    task_memory: TaskMemory = field(
        default=Factory(lambda self: TaskMemory(), takes_self=True),
        kw_only=True,
    )
    meta_memory: MetaMemory = field(default=Factory(lambda: MetaMemory()), kw_only=True)
    fail_fast: bool = field(default=True, kw_only=True)
    _execution_args: tuple = ()

    @rulesets.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_rulesets(self, _: Attribute, rulesets: list[Ruleset]) -> None:
        if not rulesets:
            return

        if self.rules:
            raise ValueError("can't have both rulesets and rules specified")

    @rules.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_rules(self, _: Attribute, rules: list[Rule]) -> None:
        if not rules:
            return

        if self.rulesets:
            raise ValueError("can't have both rules and rulesets specified")

    def __attrs_post_init__(self) -> None:
        if self.conversation_memory is not None:
            self.conversation_memory.structure = self

        tasks = self.tasks.copy()
        self.tasks.clear()
        self.add_tasks(*tasks)

    def __add__(self, other: BaseTask | list[BaseTask]) -> list[BaseTask]:
        return self.add_tasks(*other) if isinstance(other, list) else self + [other]

    @property
    def execution_args(self) -> tuple:
        return self._execution_args

    @property
    def input_task(self) -> Optional[BaseTask]:
        return self.tasks[0] if self.tasks else None

    @property
    def output_task(self) -> Optional[BaseTask]:
        return self.tasks[-1] if self.tasks else None

    @property
    def output(self) -> Optional[BaseArtifact]:
        return self.output_task.output if self.output_task is not None else None

    @property
    def finished_tasks(self) -> list[BaseTask]:
        return [s for s in self.tasks if s.is_finished()]

    def is_finished(self) -> bool:
        return all(s.is_finished() for s in self.tasks)

    def is_executing(self) -> bool:
        return any(s for s in self.tasks if s.is_executing())

    def find_task(self, task_id: str) -> BaseTask:
        if (task := self.try_find_task(task_id)) is not None:
            return task
        raise ValueError(f"Task with id {task_id} doesn't exist.")

    def try_find_task(self, task_id: str) -> Optional[BaseTask]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        return [self.add_task(s) for s in tasks]

    def context(self, task: BaseTask) -> dict[str, Any]:
        return {"args": self.execution_args, "structure": self}

    def resolve_relationships(self) -> None:
        task_by_id = {}
        for task in self.tasks:
            if task.id in task_by_id:
                raise ValueError(f"Duplicate task with id {task.id} found.")
            task_by_id[task.id] = task

        for task in self.tasks:
            # Ensure parents include this task as a child
            for parent_id in task.parent_ids:
                if parent_id not in task_by_id:
                    raise ValueError(f"Task with id {parent_id} doesn't exist.")
                parent = task_by_id[parent_id]
                if task.id not in parent.child_ids:
                    parent.child_ids.append(task.id)

            # Ensure children include this task as a parent
            for child_id in task.child_ids:
                if child_id not in task_by_id:
                    raise ValueError(f"Task with id {child_id} doesn't exist.")
                child = task_by_id[child_id]
                if task.id not in child.parent_ids:
                    child.parent_ids.append(task.id)

    @observable
    def before_run(self, args: Any) -> None:
        self._execution_args = args

        [task.reset() for task in self.tasks]

        EventBus.publish_event(
            StartStructureRunEvent(
                structure_id=self.id,
                input_task_input=self.input_task.input,
                input_task_output=self.input_task.output,
            ),
        )

        self.resolve_relationships()

    @observable
    def after_run(self) -> None:
        EventBus.publish_event(
            FinishStructureRunEvent(
                structure_id=self.id,
                output_task_input=self.output_task.input,
                output_task_output=self.output_task.output,
            ),
            flush=True,
        )

    @abstractmethod
    def add_task(self, task: BaseTask) -> BaseTask: ...

    @observable
    def run(self, *args) -> Structure:
        self.before_run(args)

        result = self.try_run(*args)

        self.after_run()

        return result

    @abstractmethod
    def try_run(self, *args) -> Structure: ...
