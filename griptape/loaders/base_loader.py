from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent import futures
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact


@define
class BaseLoader(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    @abstractmethod
    def load(self, *args, **kwargs) -> BaseArtifact | list[BaseArtifact]:
        ...

    @abstractmethod
    def load_collection(self, *args, **kwargs) -> dict[str, list[BaseArtifact | list[BaseArtifact]]]:
        ...
