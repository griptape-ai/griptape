from __future__ import annotations
import logging
import uuid
from typing import TYPE_CHECKING, Union
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import BaseToolMemory

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class TextToolMemory(BaseToolMemory):
    query_engine: VectorQueryEngine = field(
        kw_only=True,
        default=Factory(lambda: VectorQueryEngine())
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
