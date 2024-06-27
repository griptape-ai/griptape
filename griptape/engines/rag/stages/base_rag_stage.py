from abc import ABC, abstractmethod
from concurrent import futures
from attrs import define, field, Factory
from griptape.engines.rag import RagContext


@define(kw_only=True)
class BaseRagStage(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()))

    @abstractmethod
    def run(self, context: RagContext) -> RagContext: ...
