from collections.abc import Sequence

from attrs import define

from griptape.artifacts import BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRerankRagModule


@define(kw_only=True)
class TextChunksRerankRagModule(BaseRerankRagModule):
    def run(self, context: RagContext) -> Sequence[BaseArtifact]:
        return self.rerank_driver.run(context.query, context.text_chunks)
