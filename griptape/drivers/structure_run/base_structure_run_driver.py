from abc import ABC, abstractmethod
from attrs import define

from griptape.artifacts.base_artifact import BaseArtifact


@define
class BaseStructureRunDriver(ABC):
    @abstractmethod
    def run(self, *args) -> BaseArtifact:
        ...
