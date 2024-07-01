from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Any, Callable
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRetrievalRagModule

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define(kw_only=True)
class VectorStoreRetrievalRagModule(BaseRetrievalRagModule):
    vector_store_driver: BaseVectorStoreDriver = field()
    query_params: dict[str, Any] = field(factory=dict)
    process_query_output_fn: Callable[[list[BaseVectorStoreDriver.Entry]], BaseArtifact] = field(
        default=Factory(lambda: lambda es: [e.to_artifact() for e in es])
    )

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        context_query_params = self.context_param(context, "query_params")
        query_params = self.query_params if context_query_params is None else context_query_params

        return self.process_query_output_fn(self.vector_store_driver.query(context.query, **query_params))
