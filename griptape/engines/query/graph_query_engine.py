from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import BaseGraphDriver
from griptape.engines import BaseQueryEngine


@define
class GraphQueryEngine(BaseQueryEngine):
    graph_driver: BaseGraphDriver = field(kw_only=True)

    def load_metadata(self, namespace: Optional[str] = None) -> dict:
        return self.graph_driver.load_metadata(namespace)

    def query(self, query: str, namespace: Optional[str] = None, **kwargs) -> TextArtifact:
        return self.graph_driver.query(query, namespace)

    def load_artifacts(self, namespace: Optional[str] = None) -> ListArtifact:
        return self.graph_driver.load_artifacts(namespace)

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        return self.graph_driver.upsert_text_artifact(artifact, namespace)

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> list[str]:
        return self.graph_driver.upsert_text_artifacts(artifacts, namespace)
