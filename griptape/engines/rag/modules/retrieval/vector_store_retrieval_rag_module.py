from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Optional, Sequence
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
    namespace: Optional[str] = field(default=None)
    top_n: Optional[int] = field(default=None)

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        all_queries = [context.query] + context.alternative_queries
        namespace = context.module_params.get("namespace") if self.namespace is None else self.namespace

        with self.futures_executor_fn() as executor:
            results = utils.execute_futures_list(
                [
                    executor.submit(self.vector_store_driver.query, query, self.top_n, namespace, False)
                    for query in all_queries
                ]
            )

        return [
            artifact
            for artifact in [r.to_artifact() for r in list(itertools.chain.from_iterable(results))]
            if isinstance(artifact, TextArtifact)
        ]
