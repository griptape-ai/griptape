from attr import define, field, Factory
from typing import Any
from griptape.artifacts import TextArtifact
from griptape.engines import BaseQueryEngine
from griptape.loaders import TextLoader
from griptape.tasks import BaseTextInputTask


@define
class TextQueryTask(BaseTextInputTask):
    query_engine: BaseQueryEngine = field(kw_only=True)
    loader: TextLoader = field(
        default=Factory(lambda: TextLoader()), kw_only=True
    )
    namespace: str = field(kw_only=True)

    def run(self) -> TextArtifact:
        return self.query_engine.query(
            self.input.to_text(), namespace=self.namespace
        )

    def load(self, content: Any) -> list[TextArtifact]:
        artifacts = self.loader.load(content)

        self.query_engine.upsert_text_artifacts(
            artifacts, namespace=self.namespace
        )

        return artifacts
