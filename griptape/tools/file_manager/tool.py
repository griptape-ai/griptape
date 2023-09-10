from __future__ import annotations
import os
from attr import define, field
from griptape.artifacts import ErrorArtifact, BlobArtifact, InfoArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
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
    def load_files_from_disk(self, params: dict) -> ListArtifact | ErrorArtifact:
        list_artifact = ListArtifact()

        for path in params["values"]["paths"]:
            file_name = os.path.basename(path)
            dir_name = os.path.dirname(path)
            full_path = os.path.join(self.dir, path)

            try:
                with open(full_path, "rb") as file:
                    list_artifact.value.append(
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

        return list_artifact

    @activity(config={
        "description": "Can be used to save memory artifacts to disk",
        "schema": Schema(
            {
                Literal(
                    "dirname",
                    description="Destination directory name on disk in the POSIX format. For example, 'foo/bar'"
                ): str,
                Literal(
                    "filename",
                    description="Destination filename. For example, 'baz.txt'"
                ): str,
                "memory_name": str,
                "artifact_namespace": str
            }
        )
    })
    def save_memory_artifacts_to_disk(self, params: dict) -> ErrorArtifact | InfoArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        dirname = params["values"]["dirname"]
        filename = params["values"]["filename"]

        if memory:
            artifacts = memory.load_artifacts(artifact_namespace)

            if len(artifacts) == 0:
                return ErrorArtifact("no artifacts found")
            elif len(artifacts) == 1:
                try:
                    self._save_to_disk(
                        os.path.join(self.dir, dirname, filename),
                        artifacts[0].to_text()
                    )

                    return InfoArtifact(f"saved successfully")
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")
            else:
                try:
                    for a in artifacts:
                        self._save_to_disk(
                            os.path.join(self.dir, dirname, f"{a.name}-{filename}"),
                            a.to_text()
                        )

                    return InfoArtifact(f"saved successfully")
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to save content to a file",
        "schema": Schema(
            {
                Literal(
                    "path",
                    description="Destination file path on disk in the POSIX format. For example, 'foo/bar/baz.txt'"
                ): str,
                "content": str
            }
        )
    })
    def save_content_to_file(self, params: dict) -> ErrorArtifact | InfoArtifact:
        content = params["values"]["content"]
        new_path = params["values"]["path"]
        full_path = os.path.join(self.dir, new_path)

        try:
            self._save_to_disk(full_path, content)

            return InfoArtifact(f"saved successfully")
        except Exception as e:
            return ErrorArtifact(f"error writing file to disk: {e}")

    def _save_to_disk(self, path: str, value: any) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as file:
            file.write(value.encode() if isinstance(value, str) else value)
