from abc import ABC, abstractmethod
from attrs import define
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseModule


@define(kw_only=True)
class BaseQueryModule(BaseModule, ABC):
    @abstractmethod
    def run(self, context: RagContext) -> list[str]: ...
