from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Sequence, Any
from attrs import define, field
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

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        all_queries = [context.query] + context.alternative_queries
        context_query_params = self.context_param(context, "query_params")
        query_params = self.query_params if context_query_params is None else context_query_params

        with self.futures_executor_fn() as executor:
            futures_list = [
                executor.submit(self.vector_store_driver.query, query, **query_params)
                for query in all_queries
            ]

            results = utils.execute_futures_list(futures_list)

        return [
            artifact
            for artifact in [r.to_artifact() for r in list(itertools.chain.from_iterable(results))]
            if isinstance(artifact, TextArtifact)
        ]
