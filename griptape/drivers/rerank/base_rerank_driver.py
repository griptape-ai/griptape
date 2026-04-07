from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact


@define(kw_only=True)
class BaseRerankDriver(ABC):
    @abstractmethod
    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]: ...
