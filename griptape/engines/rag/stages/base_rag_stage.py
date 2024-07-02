from abc import ABC, abstractmethod
from concurrent import futures
from typing import Callable
from attrs import define, field, Factory
from griptape.engines.rag import RagContext


@define(kw_only=True)
class BaseRagStage(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor())
    )

    @abstractmethod
    def run(self, context: RagContext) -> RagContext: ...
