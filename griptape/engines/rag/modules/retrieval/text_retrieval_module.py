from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules.retrieval import BaseRetrievalModule

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define
class TextRetrievalModule(BaseRetrievalModule):
    namespace: Optional[str] = field(default=None, kw_only=True)
    top_n: Optional[int] = field(default=None, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)

    def run(self, context: RagContext) -> list[TextArtifact]:
        all_queries = [context.initial_query] + context.alternative_queries
        namespace = self.namespace or context.namespace

        results = utils.execute_futures_list(


            [
                self.futures_executor.submit(self.vector_store_driver.query, query, self.top_n, namespace, False)
                for query in all_queries
            ]
        )

        return [
            artifact
            for artifact in [r.to_artifact() for r in list(itertools.chain.from_iterable(results))]
            if isinstance(artifact, TextArtifact)
        ]
