from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.engines import BaseQueryEngine, VectorQueryEngine
from griptape.loaders import BaseLoader, TextLoader
from griptape.tasks import BaseTextInputTask


@define
class TextQueryTask(BaseTextInputTask):
    query_engine: BaseQueryEngine = field(
        default=Factory(lambda: VectorQueryEngine()),
        kw_only=True
    )
    loader: BaseLoader = field(
        default=Factory(lambda: TextLoader()),
        kw_only=True
    )

    def run(self) -> TextArtifact:
        return self.query_engine.query(self.input.to_text())

    def load(self, content: any, namespace: str) -> list[TextArtifact]:
        artifacts = self.loader.load(content)

        self.query_engine.upsert_text_artifacts(
            artifacts,
            namespace=namespace
        )

        return artifacts
