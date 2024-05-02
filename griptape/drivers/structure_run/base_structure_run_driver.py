from abc import ABC, abstractmethod

from attrs import define

from griptape.artifacts import BaseArtifact


@define
class BaseStructureRunDriver(ABC):
    def run(self, *args: BaseArtifact) -> BaseArtifact:
        return self.try_run(*args)

    @abstractmethod
    def try_run(self, *args: BaseArtifact) -> BaseArtifact:
        ...
