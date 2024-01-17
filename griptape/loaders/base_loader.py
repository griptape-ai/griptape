from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent import futures
from typing import Any
from collections.abc import Mapping, Sequence

from attr import define, field, Factory

from griptape.artifacts import BaseArtifact


@define
class BaseLoader(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    @abstractmethod
    def load(self, source: Any, *args, **kwargs) -> BaseArtifact | Sequence[BaseArtifact]:
        ...

    @abstractmethod
    def load_collection(
        self, sources: list[Any], *args, **kwargs
    ) -> Mapping[str, BaseArtifact | Sequence[BaseArtifact | Sequence[BaseArtifact]]]:
        ...
