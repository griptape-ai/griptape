from abc import ABC, abstractmethod
from attr import define, field
from griptape.artifacts import BaseArtifact
from griptape.drivers import BaseRerankDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseModule


@define(kw_only=True)
class BaseRerankModule(BaseModule, ABC):
    rerank_driver: BaseRerankDriver = field()

    @abstractmethod
    def run(self, context: RagContext) -> list[BaseArtifact]:
        ...
