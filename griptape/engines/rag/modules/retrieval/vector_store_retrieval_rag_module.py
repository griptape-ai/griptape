from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Any
from attrs import define, field
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRetrievalRagModule

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define(kw_only=True)
class VectorStoreRetrievalRagModule(BaseRetrievalRagModule):
    vector_store_driver: BaseVectorStoreDriver = field()
    query_params: dict[str, Any] = field(factory=dict)

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        context_query_params = self.context_param(context, "query_params")
        query_params = self.query_params if context_query_params is None else context_query_params

        results = self.vector_store_driver.query(context.query, **query_params)

        return [
            artifact
            for artifact in [r.to_artifact() for r in results]
            if isinstance(artifact, TextArtifact)
        ]
