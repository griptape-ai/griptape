from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.data.modules import BaseModule

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define
class TextRetrieverModule(BaseModule):
    namespace: Optional[str] = field(default=None, kw_only=True)
    top_n: Optional[int] = field(default=None, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)

    def process(self, context: dict) -> dict:
        query = context.get("query")

        if query:
            result = self.vector_store_driver.query(query, self.top_n, self.namespace)
            artifacts = [
                artifact
                for artifact in [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta]
                if isinstance(artifact, TextArtifact)
            ]

            context["text_artifact_chunks"] = artifacts

        return context
