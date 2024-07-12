from __future__ import annotations

import os

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.drivers import BaseFileManagerDriver, LocalFileManagerDriver
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class FileManager(BaseTool):
    """FileManager is a tool that can be used to list, load, and save files.

    Attributes:
        file_manager_driver: File Manager Driver to use to list, load, and save files.
    """

    file_manager_driver: BaseFileManagerDriver = field(default=Factory(lambda: LocalFileManagerDriver()), kw_only=True)

    @activity(
        config={
            "description": "Can be used to list files on disk",
            "schema": Schema(
                {Literal("path", description="Relative path in the POSIX format. For example, 'foo/bar'"): str},
            ),
        },
    )
    def list_files_from_disk(self, params: dict) -> TextArtifact | ErrorArtifact:
        path = params["values"]["path"]
        return self.file_manager_driver.list_files(path)

    @activity(
        config={
            "description": "Can be used to load files from disk",
            "schema": Schema(
                {
                    Literal(
                        "paths",
                        description="Relative paths to files to be loaded in the POSIX format. For example, ['foo/bar/file.txt']",
                    ): list[str],
                },
            ),
        },
    )
    def load_files_from_disk(self, params: dict) -> ListArtifact | ErrorArtifact:
        paths = params["values"]["paths"]
        artifacts = []

        for path in paths:
            artifact = self.file_manager_driver.load_file(path)
            if isinstance(artifact, ListArtifact):
                artifacts.extend(artifact.value)
            else:
                artifacts.append(artifact)
        return ListArtifact(artifacts)

    @activity(
        config={
            "description": "Can be used to save memory artifacts to disk",
            "schema": Schema(
                {
                    Literal(
                        "dir_name",
                        description="Relative destination path name on disk in the POSIX format. For example, 'foo/bar'",
                    ): str,
                    Literal("file_name", description="Destination file name. For example, 'baz.txt'"): str,
                    "memory_name": str,
                    "artifact_namespace": str,
                },
            ),
        },
    )
    def save_memory_artifacts_to_disk(self, params: dict) -> ErrorArtifact | InfoArtifact:
        dir_name = params["values"]["dir_name"]
        file_name = params["values"]["file_name"]
        memory_name = params["values"]["memory_name"]
        artifact_namespace = params["values"]["artifact_namespace"]

        memory = self.find_input_memory(params["values"]["memory_name"])
        if not memory:
            return ErrorArtifact(f"Failed to save memory artifacts to disk - memory named '{memory_name}' not found")

        list_artifact = memory.load_artifacts(artifact_namespace)

        if len(list_artifact) == 0:
            return ErrorArtifact(
                f"Failed to save memory artifacts to disk - memory named '{memory_name}' does not contain any artifacts",
            )

        for artifact in list_artifact.value:
            formatted_file_name = f"{artifact.name}-{file_name}" if len(list_artifact) > 1 else file_name
            result = self.file_manager_driver.save_file(os.path.join(dir_name, formatted_file_name), artifact.value)
            if isinstance(result, ErrorArtifact):
                return result

        return InfoArtifact("Successfully saved memory artifacts to disk")

    @activity(
        config={
            "description": "Can be used to save content to a file",
            "schema": Schema(
                {
                    Literal(
                        "path",
                        description="Destination file path on disk in the POSIX format. For example, 'foo/bar/baz.txt'",
                    ): str,
                    "content": str,
                },
            ),
        },
    )
    def save_content_to_file(self, params: dict) -> ErrorArtifact | InfoArtifact:
        path = params["values"]["path"]
        content = params["values"]["content"]
        return self.file_manager_driver.save_file(path, content)
