from __future__ import annotations

import logging
from typing import Optional

from attrs import define, field

from griptape.configs import Defaults
from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseSubtask(BaseTask):
    _origin_task: Optional[BaseTask] = field(default=None, kw_only=True)

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

    def add_child(self, child: BaseTask) -> BaseTask:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)
        return child

    def add_parent(self, parent: BaseTask) -> BaseTask:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)
        return parent

    def attach_to(self, parent_task: BaseTask) -> None:
        self._origin_task = parent_task
