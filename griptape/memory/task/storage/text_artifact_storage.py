from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from attrs import define, field
from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact
from griptape.drivers import BaseVectorStoreDriver
from griptape.engines.rag import RagEngine, RagContext
from griptape.memory.task.storage import BaseArtifactStorage

if TYPE_CHECKING:
    from griptape.engines import BaseSummaryEngine, CsvExtractionEngine, JsonExtractionEngine


@define(kw_only=True)
class TextArtifactStorage(BaseArtifactStorage):
    vector_store_driver: BaseVectorStoreDriver = field()
    rag_engine: Optional[RagEngine] = field(default=None)
    summary_engine: Optional[BaseSummaryEngine] = field( default=None)
    csv_extraction_engine: Optional[CsvExtractionEngine] = field(default=None)
    json_extraction_engine: Optional[JsonExtractionEngine] = field(default=None)

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, TextArtifact)

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        if isinstance(artifact, TextArtifact):
            self.vector_store_driver.upsert_text_artifact(artifact, namespace)
        else:
            raise ValueError("Artifact must be of instance TextArtifact")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return self.vector_store_driver.load_artifacts(namespace)

    def summarize(self, namespace: str) -> TextArtifact:
        if self.summary_engine is None:
            raise ValueError("Summary engine is not set.")

        return self.summary_engine.summarize_artifacts(self.load_artifacts(namespace))

    def query(self, namespace: str, query: str, metadata: Any = None) -> TextArtifact:
        if self.rag_engine is None:
            raise ValueError("RAG engine is not set.")

        return self.rag_engine.process(
            RagContext(
                initial_query=query,
                namespace=namespace,
                metadata=None if metadata is None else str(metadata)
            )
        ).output
