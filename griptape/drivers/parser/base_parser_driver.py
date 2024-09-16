from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from attrs import define

from griptape.artifacts.base_artifact import BaseArtifact

T = TypeVar("T", bound=BaseArtifact)


@define()
class BaseParserDriver(ABC, Generic[T]):
    def parse(self, data: Any, meta: Optional[dict] = None) -> T:
        """Converts bytes to an Artifact.

        Args:
            data: The data to parse.
            meta: Additional metadata to pass to the parser.
        """
        if meta is None:
            meta = {}
        return self.try_parse(data, meta)

    @abstractmethod
    def try_parse(self, data: Any, meta: dict) -> T: ...
