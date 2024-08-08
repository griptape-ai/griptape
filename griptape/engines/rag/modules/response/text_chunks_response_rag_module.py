from attrs import define

from griptape.artifacts import ListArtifact, BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseResponseRagModule


@define(kw_only=True)
class TextChunksResponseRagModule(BaseResponseRagModule):
    def run(self, context: RagContext) -> BaseArtifact:
        return ListArtifact(context.text_chunks)
