from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.engines.rag.modules.retrieval import BaseRetriever

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define
class TextRetriever(BaseRetriever):
    namespace: Optional[str] = field(default=None, kw_only=True)
    top_n: Optional[int] = field(default=None, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)

    def retrieve(self, query: str) -> list[TextArtifact]:
        result = self.vector_store_driver.query(query, self.top_n, self.namespace)

        return [
            artifact
            for artifact in [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta]
            if isinstance(artifact, TextArtifact)
        ]
