from griptape.artifacts import BaseArtifact
from griptape.memory import TaskMemory


def load_artifact_from_memory(
    memory: TaskMemory,
    artifact_namespace: str,
    artifact_name: str,
    artifact_type: type,
) -> BaseArtifact:
    if memory is None:
        raise ValueError("memory not found")

    artifacts = memory.load_artifacts(namespace=artifact_namespace)
    if len(artifacts) == 0:
        raise ValueError("no artifacts found in namespace")

    try:
        artifact = [a for a in artifacts if a.name == artifact_name][0]
    except IndexError as exc:
        raise ValueError(f"artifact {artifact_name} not found in namespace {artifact_namespace}") from exc

    if not isinstance(artifact, artifact_type):
        raise ValueError(f"{artifact.name} is not of type {artifact_type}")

    return artifact
