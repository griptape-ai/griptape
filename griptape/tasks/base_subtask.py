from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Optional, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.configs import Defaults
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks.base_task import BaseTask

if TYPE_CHECKING:
    from griptape.common import PromptStack
    from griptape.drivers import BasePromptDriver

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseSubtask(BaseTask):
    _origin_task: Optional[BaseTask] = field(default=None, kw_only=True, alias="origin_task")
    _input: Union[BaseArtifact, Callable[[BaseSubtask], BaseArtifact]] = field(alias="input")

    @property
    def origin_task(self) -> BaseTask:
        if self._origin_task is not None:
            return self._origin_task
        else:
            raise Exception("ActionSubtask has no origin task.")

    @property
    def parents(self) -> list[BaseTask]:
        if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
            return [self.origin_task.find_subtask(parent_id) for parent_id in self.parent_ids]
        else:
            raise Exception("ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin.")

    @property
    def children(self) -> list[BaseTask]:
        if isinstance(self.origin_task, ActionsSubtaskOriginMixin):
            return [self.origin_task.find_subtask(child_id) for child_id in self.child_ids]
        else:
            raise Exception("ActionSubtask must be attached to a Task that implements ActionSubtaskOriginMixin.")

    def __str__(self) -> str:
        return self.to_text()

    @abstractmethod
    def to_text(self) -> str: ...

    @abstractmethod
    def add_to_prompt_stack(self, prompt_driver: BasePromptDriver, prompt_stack: PromptStack) -> None: ...

    @abstractmethod
    def should_run(self) -> bool: ...

    def attach_to(self, parent_task: BaseTask) -> BaseSubtask:
        self._origin_task = parent_task

        return self

    def add_child(self, child: BaseTask) -> BaseTask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)
        return child

    def add_parent(self, parent: BaseTask) -> BaseTask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)
        return parent

    def before_run(self) -> None:
        logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.value)

    def after_run(self) -> None:
        output = self.output.to_text() if isinstance(self.output, BaseArtifact) else str(self.output)

        logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, output)
