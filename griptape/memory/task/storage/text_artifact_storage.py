from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import Attribute, define, field

from griptape.artifacts import BaseArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.engines.rag import RagContext, RagEngine
from griptape.memory.task.storage import BaseArtifactStorage

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver
    from griptape.engines import BaseSummaryEngine, CsvExtractionEngine, JsonExtractionEngine


@define(kw_only=True)
class TextArtifactStorage(BaseArtifactStorage):
    vector_store_driver: BaseVectorStoreDriver = field()
    rag_engine: Optional[RagEngine] = field(default=None)
    retrieval_rag_module_name: Optional[str] = field(default=None)
    summary_engine: Optional[BaseSummaryEngine] = field(default=None)
    csv_extraction_engine: Optional[CsvExtractionEngine] = field(default=None)
    json_extraction_engine: Optional[JsonExtractionEngine] = field(default=None)

    @rag_engine.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_rag_engine(self, _: Attribute, rag_engine: str) -> None:
        if rag_engine is not None and self.retrieval_rag_module_name is None:
            raise ValueError("You have to set retrieval_rag_module_name if rag_engine is provided")

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, TextArtifact)

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        if isinstance(artifact, TextArtifact):
            self.vector_store_driver.upsert_text_artifact(artifact, namespace=namespace)
        else:
            raise ValueError("Artifact must be of instance TextArtifact")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return self.vector_store_driver.load_artifacts(namespace=namespace)

    def summarize(self, namespace: str) -> TextArtifact:
        if self.summary_engine is None:
            raise ValueError("Summary engine is not set.")

        return self.summary_engine.summarize_artifacts(self.load_artifacts(namespace))

    def query(self, namespace: str, query: str, metadata: Any = None) -> BaseArtifact:
        if self.rag_engine is None:
            raise ValueError("rag_engine is not set")

        if self.retrieval_rag_module_name is None:
            raise ValueError("retrieval_rag_module_name is not set")

        result = self.rag_engine.process(
            RagContext(
                query=query,
                module_configs={
                    self.retrieval_rag_module_name: {
                        "query_params": {
                            "namespace": namespace,
                            "metadata": None if metadata is None else str(metadata),
                        },
                    },
                },
            ),
        ).output

        if result is None:
            return InfoArtifact("Empty output")
        else:
            return result
