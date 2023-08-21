from __future__ import annotations
import os
from attr import define, field
from griptape.artifacts import ErrorArtifact, BlobArtifact, InfoArtifact
from griptape.tools import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


@define
class FileManager(BaseTool):
    dir: str = field(default=os.getcwd(), kw_only=True)

    @activity(config={
        "description": "Can be used to load files from disk",
        "schema": Schema({
            Literal(
                "paths",
                description="Paths to files to be loaded in the POSIX format. For example, ['foo/bar/file.txt']"
            ): []
        })
    })
    def load_files_from_disk(self, params: dict) -> list[BlobArtifact] | ErrorArtifact:
        artifact_list = []

        for path in params["values"]["paths"]:
            file_name = os.path.basename(path)
            dir_name = os.path.dirname(path)
            full_path = os.path.join(self.dir, path)

            try:
                with open(full_path, "rb") as file:
                    artifact_list.append(
                        BlobArtifact(
                            file.read(),
                            name=file_name,
                            dir=dir_name
                        )
                    )
            except FileNotFoundError:
                return ErrorArtifact(f"file {file_name} not found")
            except Exception as e:
                return ErrorArtifact(f"error loading file: {e}")

        return artifact_list

    @activity(config={
        "description": "Can be used to save an artifact namespace to disk",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            Literal(
                "path",
                description="Destination path on disk in the POSIX format. For example, ['foo/bar/file.txt']"
            ): str
        })
    })
    def save_file_to_disk(self, params: dict) -> ErrorArtifact | InfoArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        new_path = params["values"]["path"]
        memory = self.find_input_memory(params["values"]["memory_name"])

        if memory:
            artifacts = memory.load_artifacts(artifact_namespace)

            if len(artifacts) == 0:
                return ErrorArtifact("no artifacts found")
            else:
                try:
                    full_path = os.path.join(self.dir, new_path)

                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    with open(full_path, "wb") as file:
                        value = "\n".join([a.to_text() for a in artifacts])

                        file.write(value.encode() if isinstance(value, str) else value)

                        return InfoArtifact(f"saved successfully")
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")
        else:
            return ErrorArtifact("memory not found")
