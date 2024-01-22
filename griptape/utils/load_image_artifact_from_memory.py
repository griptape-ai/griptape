from griptape.artifacts import ImageArtifact
from griptape.memory import TaskMemory


def load_image_artifact_from_memory(memory: TaskMemory, artifact_namespace: str, artifact_name: str) -> ImageArtifact:
    if memory is None:
        raise ValueError("memory not found")

    artifacts = memory.load_artifacts(namespace=artifact_namespace)
    if len(artifacts) == 0:
        raise ValueError("no artifacts found in namespace")

    try:
        artifact = [a for a in artifacts if a.name == artifact_name][0]
    except IndexError:
        raise ValueError(f"artifact {artifact_name} not found in namespace {artifact_namespace}")

    if not isinstance(artifact, ImageArtifact):
        raise ValueError(f"{artifact.name} is not an ImageArtifact")

    return artifact
