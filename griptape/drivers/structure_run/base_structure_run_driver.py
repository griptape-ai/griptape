from abc import ABC, abstractmethod

from attr import field
from attrs import define

from griptape.artifacts import BaseArtifact


@define
class BaseStructureRunDriver(ABC):
    env: dict[str, str] = field(default={}, kw_only=True)

    def run(self, *args: BaseArtifact) -> BaseArtifact:
        return self.try_run(*args)

    @abstractmethod
    def try_run(self, *args: BaseArtifact) -> BaseArtifact: ...
