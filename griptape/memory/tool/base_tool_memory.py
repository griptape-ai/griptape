from abc import ABC, abstractmethod
from typing import Union
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact
from griptape.core import ActivityMixin


@define
class BaseToolMemory(ActivityMixin, ABC):
    id: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_output(
            self,
            tool_activity: callable,
            artifact: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        return artifact

    @abstractmethod
    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...
    