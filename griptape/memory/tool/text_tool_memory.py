import logging
import uuid
from typing import Union
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import BaseToolMemory


@define
class TextToolMemory(BaseToolMemory):
    query_engine: VectorQueryEngine = field(
        kw_only=True,
        default=Factory(lambda: VectorQueryEngine())
    )
    top_n: int = field(default=5, kw_only=True)

    def process_output(
            self,
            tool_activity: callable,
            value: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(value, TextArtifact):
            namespace = value.id

            self.query_engine.vector_driver.upsert_text_artifact(value, namespace=namespace)
        elif isinstance(value, list):
            artifacts = [a for a in value if isinstance(a, TextArtifact)]

            if len(artifacts) > 0:
                namespace = uuid.uuid4().hex

                [self.query_engine.vector_driver.upsert_text_artifact(
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
            for e in self.query_engine.vector_driver.load_entries(namespace)
        ]
