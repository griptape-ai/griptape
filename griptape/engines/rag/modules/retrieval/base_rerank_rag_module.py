from abc import ABC, abstractmethod
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.drivers import BaseRerankDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRagModule


@define(kw_only=True)
class BaseRerankRagModule(BaseRagModule, ABC):
    rerank_driver: BaseRerankDriver = field()

    @abstractmethod
    def run(self, context: RagContext) -> Sequence[BaseArtifact]: ...
