from attrs import define

from griptape.artifacts import ListArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseResponseRagModule


@define(kw_only=True)
class TextChunksResponseRagModule(BaseResponseRagModule):
    def run(self, context: RagContext) -> RagContext:
        context.output = ListArtifact(context.text_chunks)

        return context
