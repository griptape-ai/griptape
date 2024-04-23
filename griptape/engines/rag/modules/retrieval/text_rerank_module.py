from attr import define
from griptape.artifacts import BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRerankModule


@define(kw_only=True)
class TextRerankModule(BaseRerankModule):
    def run(self, context: RagContext) -> list[BaseArtifact]:
        return self.rerank_driver.run(context.initial_query, context.text_chunks)
