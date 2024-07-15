from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import Factory, define, field

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class BaseStructureRunDriver(ABC):
    """Base class for Structure Run Drivers.

    Attributes:
        env: Environment variables to set before running the Structure.
    """

    env: dict[str, str] = field(default=Factory(dict), kw_only=True)

    def run(self, *args: BaseArtifact) -> BaseArtifact:
        return self.try_run(*args)

    @abstractmethod
    def try_run(self, *args: BaseArtifact) -> BaseArtifact: ...
