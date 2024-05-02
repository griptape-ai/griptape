from abc import ABC, abstractmethod

from attrs import define

from griptape.artifacts import BaseArtifact, ErrorArtifact


@define
class BaseStructureRunDriver(ABC):
    def run(self, *args: BaseArtifact) -> BaseArtifact:
        try:
            return self.try_run(*args)
        except Exception as e:
            return ErrorArtifact(str(e))

    @abstractmethod
    def try_run(self, *args: BaseArtifact) -> BaseArtifact:
        ...
