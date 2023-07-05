from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Union, Optional
from abc import ABC, abstractmethod
from attr import define, field, Factory

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.tasks import ActionSubtask


@define
class BaseToolMemory(ABC):
    id: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    namespace_metadata: dict[str, str] = field(factory=dict, kw_only=True)

    def process_output(
            self,
            tool_activity: callable,
            subtask: ActionSubtask,
            artifact: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        return artifact

    @abstractmethod
    def load_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...

    def load_and_combine_artifacts(self, namespace: str) -> Optional[BaseArtifact]:
        artifacts = self.load_artifacts(namespace)

        if len(artifacts) > 0:
            return reduce(lambda a, b: a + b, artifacts[1:], artifacts[0])
        else:
            return None
