from attr import define, field
from griptape.drivers import BaseRerankDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRetrievalModule


@define(kw_only=True)
class TextReranker(BaseRetrievalModule):
    rerank_driver: BaseRerankDriver = field()

    def run(self, context: RagContext) -> RagContext:
        ...
