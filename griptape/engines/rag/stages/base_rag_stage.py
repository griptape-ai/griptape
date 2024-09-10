from abc import ABC, abstractmethod
from collections.abc import Sequence

from attrs import define

from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRagModule
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin


@define(kw_only=True)
class BaseRagStage(FuturesExecutorMixin, ABC):
    @abstractmethod
    def run(self, context: RagContext) -> RagContext: ...

    @property
    @abstractmethod
    def modules(self) -> Sequence[BaseRagModule]: ...
