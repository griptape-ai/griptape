from typing import Union, Optional
from attr import define, field, Factory
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.core.decorators import activity
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import BaseToolMemory


@define
class TextToolMemory(BaseToolMemory):
    allowlist: Optional[list[str]] = field(
        default=Factory(lambda: ["save"]),
        kw_only=True
    )
    query_engine: VectorQueryEngine = field(
        kw_only=True,
        default=Factory(lambda: VectorQueryEngine())
    )
    top_n: int = field(default=5, kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> Union[InfoArtifact, ErrorArtifact]:
        from griptape.utils import J2

        if isinstance(artifact, TextArtifact):
            artifact_ids = [self.query_engine.vector_driver.upsert_text_artifact(artifact, namespace=self.namespace)]
        elif isinstance(artifact, ListArtifact):
            artifact_ids = [
                self.query_engine.vector_driver.upsert_text_artifact(
                    a, namespace=self.namespace
                ) for a in artifact.value if isinstance(a, TextArtifact)
            ]
        else:
            artifact_ids = []

        if len(artifact_ids) > 0:
            output = J2("memory/tool/text.j2").render(
                memory_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.name,
                artifact_ids=str.join(", ", artifact_ids)
            )

            return InfoArtifact(output)
        else:
            return artifact

    def load_artifact(self, name: str) -> Union[TextArtifact, ErrorArtifact]:
        value = self.query_engine.vector_driver.load_vector(name, namespace=self.namespace)

        if value:
            return TextArtifact(value)
        else:
            return ErrorArtifact(f"can't find artifact {name}")

    @activity(config={
        "description": "Can be used to save artifact values",
        "schema": Schema({
            "artifact_value": str
        }),
    })
    def save(self, params: dict) -> Union[InfoArtifact, ErrorArtifact]:
        artifact = TextArtifact(params["values"]["artifact_value"])
        artifact_id = self.query_engine.vector_driver.upsert_text_artifact(artifact, namespace=self.namespace)

        return InfoArtifact(f"Value was successfully stored with the following ID: {artifact_id}")

    @activity(config={
        "description": "Can be used to load artifact values",
        "schema": Schema({
            "artifact_id": str
        })
    })
    def load(self, params: dict) -> BaseArtifact:
        artifact_id = params["values"]["artifact_id"]
        value = self.query_engine.vector_driver.load_vector(artifact_id, namespace=self.namespace)

        if value:
            return BaseArtifact.from_json(value.meta["artifact"])
        else:
            return ErrorArtifact(f"can't find artifact {artifact_id}")

    @activity(config={
        "description":
            "Can be used to search artifact values",
        "schema": Schema({
            Literal(
                "query",
                description="Search query"
            ): str
        })
    })
    def query(self, params: dict) -> TextArtifact:
        query = params["values"]["query"]

        return self.query_engine.query(query, namespace=self.namespace)
