from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Any, Callable
from attrs import define, field, Factory
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRetrievalRagModule

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define(kw_only=True)
class VectorStoreRetrievalRagModule(BaseRetrievalRagModule):
    vector_store_driver: BaseVectorStoreDriver = field()
    query_params: dict[str, Any] = field(factory=dict)
    process_query_output_fn: Callable[[list[BaseVectorStoreDriver.Entry]], Sequence[TextArtifact]] = field(
        default=Factory(lambda: lambda es: [e.to_artifact() for e in es])
    )

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        query_params = utils.dict_merge(self.query_params, self.get_context_param(context, "query_params"))

        return self.process_query_output_fn(self.vector_store_driver.query(context.query, **query_params))
