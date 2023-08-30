from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union
from attr import define, field, Factory
from griptape.mixins import ActivityMixin

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.tasks import ActionSubtask


@define
class BaseToolMemory(ActivityMixin, ABC):
    name: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
    )
    namespace_metadata: dict[str, str] = field(factory=dict, kw_only=True)

    def process_output(
        self,
        _tool_activity: callable,
        _subtask: ActionSubtask,
        artifact: Union[BaseArtifact, list[BaseArtifact]],
    ) -> BaseArtifact:
        return artifact

    @abstractmethod
    def load_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...
