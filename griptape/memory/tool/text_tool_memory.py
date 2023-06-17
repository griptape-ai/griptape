import logging
import uuid
from typing import Union
from attr import define, field, Factory
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.drivers import OpenAiPromptDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import BaseToolMemory
from griptape.summarizers import PromptDriverSummarizer


@define
class TextToolMemory(BaseToolMemory):
    query_engine: VectorQueryEngine = field(
        kw_only=True,
        default=Factory(lambda: VectorQueryEngine())
    )
    top_n: int = field(default=5, kw_only=True)

    @activity(config={
        "description": "Can be used to generate summaries of memory artifacts",
        "schema": Schema({
            "artifact_namespace": str
        })
    })
    def summarize(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        artifact_namespace = params["values"]["artifact_namespace"]
        artifacts = self.load_namespace_artifacts(artifact_namespace)

        if len(artifacts) == 0:
            return ErrorArtifact("no artifacts found")
        else:
            artifact_list = []

            for artifact in artifacts:
                try:
                    summary = PromptDriverSummarizer(
                        driver=OpenAiPromptDriver()
                    ).summarize_text(artifact.value)

                    artifact_list.append(TextArtifact(summary))
                except Exception as e:
                    return ErrorArtifact(f"error summarizing text: {e}")

            return artifact_list

    @activity(config={
        "description": "Can be used to search and query memory artifacts in a namespace",
        "schema": Schema({
            "artifact_namespace": str,
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> BaseArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        return self.query_engine.query(
            query,
            namespace=artifact_namespace
        )

    def process_output(
            self,
            tool_activity: callable,
            value: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(value, TextArtifact):
            namespace = value.id

            self.query_engine.vector_store_driver.upsert_text_artifact(value, namespace=namespace)
        elif isinstance(value, list):
            artifacts = [a for a in value if isinstance(a, TextArtifact)]

            if len(artifacts) > 0:
                namespace = uuid.uuid4().hex

                [self.query_engine.vector_store_driver.upsert_text_artifact(
                    a, namespace=namespace
                ) for a in artifacts]
            else:
                namespace = None
        else:
            namespace = None

        if namespace:
            output = J2("memory/tool/text.j2").render(
                memory_id=self.id,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        else:
            logging.info(f"Artifact {value.id} of type {value.type} can't be processed by memory {self.id}")

            return value

    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        return [
            BaseArtifact.from_json(e.meta["artifact"])
            for e in self.query_engine.vector_store_driver.load_entries(namespace)
        ]
