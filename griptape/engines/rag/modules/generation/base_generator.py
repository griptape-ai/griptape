from abc import ABC, abstractmethod
from attr import define
from griptape.engines.rag import RagContext


@define(kw_only=True)
class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, context: RagContext) -> RagContext:
        ...
