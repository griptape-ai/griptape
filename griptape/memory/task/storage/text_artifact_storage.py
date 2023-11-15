from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact
from griptape.memory.task.storage import BaseArtifactStorage

if TYPE_CHECKING:
    from griptape.engines import BaseSummaryEngine, CsvExtractionEngine, JsonExtractionEngine, VectorQueryEngine


@define
class TextArtifactStorage(BaseArtifactStorage):
    query_engine: VectorQueryEngine = field(kw_only=True)
    summary_engine: BaseSummaryEngine = field(kw_only=True)
    csv_extraction_engine: CsvExtractionEngine = field(kw_only=True)
    json_extraction_engine: JsonExtractionEngine = field(kw_only=True)

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, TextArtifact)

    def store_artifact(self, namespace: str, artifact: TextArtifact) -> None:
        self.query_engine.upsert_text_artifact(artifact, namespace)

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return self.query_engine.load_artifacts(namespace)

    def summarize(self, namespace: str) -> TextArtifact:
        return self.summary_engine.summarize_artifacts(self.load_artifacts(namespace))

    def query(self, namespace: str, query: str, metadata: any = None) -> TextArtifact:
        return self.query_engine.query(namespace=namespace, query=query, metadata=str(metadata) if metadata else None)
