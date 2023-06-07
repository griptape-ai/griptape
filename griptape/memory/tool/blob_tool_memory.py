import logging
from attr import define, field, Factory
from griptape.artifacts import BlobArtifact, BaseArtifact, InfoArtifact, ListArtifact
from griptape.drivers import BaseBlobToolMemoryDriver, MemoryBlobToolMemoryDriver
from griptape.memory.tool import BaseToolMemory


@define
class BlobToolMemory(BaseToolMemory):
    driver: BaseBlobToolMemoryDriver = field(
        default=Factory(lambda: MemoryBlobToolMemoryDriver()),
        kw_only=True
    )

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(artifact, BlobArtifact):
            namespace = artifact.id

            self.driver.save(namespace, artifact)
        elif isinstance(artifact, ListArtifact):
            namespace = artifact.id

            [self.driver.save(namespace, a) for a in artifact.value if isinstance(a, BlobArtifact)]
        else:
            namespace = None

        if namespace:
            output = J2("memory/tool/blob.j2").render(
                memory_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        else:
            logging.warning(f"Artifact {artifact.id} of type {artifact.type} can't be processed by memory {self.name}")

            return artifact

    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        return self.driver.load(namespace)
