from attrs import define

from griptape.artifacts import BaseArtifact, ListArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseResponseRagModule


@define(kw_only=True)
class TextChunksResponseRagModule(BaseResponseRagModule):
    def run(self, context: RagContext) -> BaseArtifact:
        return ListArtifact(context.text_chunks)
