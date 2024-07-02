from abc import ABC, abstractmethod
from concurrent import futures
from typing import Callable
from attrs import define, field, Factory
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRagModule


@define(kw_only=True)
class BaseRagStage(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor())
    )

    @abstractmethod
    def run(self, context: RagContext) -> RagContext: ...

    @property
    @abstractmethod
    def modules(self) -> list[BaseRagModule]: ...
