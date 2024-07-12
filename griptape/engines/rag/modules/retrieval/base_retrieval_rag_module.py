from abc import ABC, abstractmethod
from collections.abc import Sequence

from attrs import define

from griptape.artifacts import BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRagModule


@define(kw_only=True)
class BaseRetrievalRagModule(BaseRagModule, ABC):
    @abstractmethod
    def run(self, context: RagContext) -> Sequence[BaseArtifact]: ...
