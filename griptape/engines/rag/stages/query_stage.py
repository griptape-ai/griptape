from attr import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class QueryStage(BaseStage):
    def run(self, context: RagContext) -> RagContext:
        return context
