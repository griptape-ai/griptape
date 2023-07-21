from __future__ import annotations
import logging
import uuid
from typing import TYPE_CHECKING, Union
from attr import define, field, Factory
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.engines import VectorQueryEngine, BaseSummaryEngine, PromptSummaryEngine
from griptape.memory.tool import BaseToolMemory

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class TextToolMemory(BaseToolMemory):
    query_engine: VectorQueryEngine = field(
        kw_only=True,
        default=Factory(lambda: VectorQueryEngine())
    )
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )

    @activity(config={
        "description": "Can be used to insert text into a memory",
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str,
            "text": str
        })
    })
    def insert(self, params: dict):
        artifact_namespace = params["values"]["artifact_namespace"]
        text = params["values"]["text"]

        self.query_engine.upsert_text_artifact(TextArtifact(text), artifact_namespace)

        return InfoArtifact("text was successfully inserted")

    @activity(config={
        "description": "Can be used to summarize memory",
        "uses_default_memory": False,
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str
        })
    })
    def summarize(self, params: dict) -> TextArtifact | ErrorArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]

        return self.summary_engine.summarize_artifacts(
            self.load_artifacts(artifact_namespace),
        )

    @activity(config={
        "description": "Can be used to search memory",
        "uses_default_memory": False,
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str,
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> TextArtifact | ErrorArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        return self.query_engine.query(
            query,
            metadata=self.namespace_metadata.get(artifact_namespace),
            namespace=artifact_namespace
        )

    def process_output(
            self,
            tool_activity: callable,
            subtask: ActionSubtask,
            value: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name

        if isinstance(value, TextArtifact):
            namespace = value.id

            self.query_engine.upsert_text_artifact(
                value,
                namespace=namespace
            )
        elif isinstance(value, list):
            artifacts = [a for a in value if isinstance(a, TextArtifact)]

            if len(artifacts) > 0:
                namespace = uuid.uuid4().hex

                self.query_engine.upsert_text_artifacts(artifacts, namespace)
            else:
                namespace = None
        else:
            namespace = None

        if namespace:
            self.namespace_metadata[namespace] = subtask.to_json()

            output = J2("memory/tool/text.j2").render(
                memory_id=self.id,
                tool_name=tool_name,
                activity_name=activity_name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        else:
            logging.info(f"Output of {tool_name}.{activity_name} can't be processed by memory {self.id}")

            return value

    def load_artifacts(self, namespace: str) -> list[TextArtifact]:
        artifacts = [
            BaseArtifact.from_json(e.meta["artifact"])
            for e in self.query_engine.vector_store_driver.load_entries(namespace)
        ]

        return [a for a in artifacts if isinstance(a, TextArtifact)]
