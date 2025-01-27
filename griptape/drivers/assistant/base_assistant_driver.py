from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, TextArtifact


@define
class BaseAssistantDriver(ABC):
    """Base class for AssistantDrivers."""

    def run(self, *args: BaseArtifact) -> TextArtifact:
        return self.try_run(*args)

    @abstractmethod
    def try_run(self, *args: BaseArtifact) -> TextArtifact: ...
