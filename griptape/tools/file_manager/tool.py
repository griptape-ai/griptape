from __future__ import annotations

import os

from attrs import Factory, define, field
from schema import Literal, Schema

import griptape.loaders as loaders
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.drivers import BaseFileManagerDriver, LocalFileManagerDriver
from griptape.loaders.blob_loader import BlobLoader
from griptape.tools import BaseTool
from griptape.utils import get_mime_type
from griptape.utils.decorators import activity


@define
class FileManagerTool(BaseTool):
    """FileManagerTool is a tool that can be used to list, load, and save files.

    Attributes:
        file_manager_driver: File Manager Driver to use to list, load, and save files.
    """

    file_manager_driver: BaseFileManagerDriver = field(default=Factory(lambda: LocalFileManagerDriver()), kw_only=True)

    loaders: dict[str, loaders.BaseLoader] = field(
        default=Factory(
            lambda self: {
                "application/pdf": loaders.PdfLoader(file_manager_driver=self.file_manager_driver),
                "text/csv": loaders.CsvLoader(file_manager_driver=self.file_manager_driver),
                "text": loaders.TextLoader(file_manager_driver=self.file_manager_driver),
                "image": loaders.ImageLoader(file_manager_driver=self.file_manager_driver),
                "application/octet-stream": BlobLoader(file_manager_driver=self.file_manager_driver),
            },
            takes_self=True,
        ),
        kw_only=True,
    )

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
                    ): Schema([str]),
                },
            ),
        },
    )
    def load_files_from_disk(self, params: dict) -> ListArtifact | ErrorArtifact:
        paths = params["values"]["paths"]
        artifacts = []

        for path in paths:
            # Fetch the file to try and determine the appropriate loader
            abs_path = os.path.join(self.file_manager_driver.workdir, path)
            mime_type = get_mime_type(abs_path)
            loader = next((loader for key, loader in self.loaders.items() if mime_type.startswith(key)))

            artifact = loader.load(path)
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
            try:
                value = artifact.value if isinstance(artifact.value, (str, bytes)) else artifact.to_text()
                self.file_manager_driver.save_file(os.path.join(dir_name, formatted_file_name), value)
            except FileNotFoundError:
                return ErrorArtifact("Path not found")
            except IsADirectoryError:
                return ErrorArtifact("Path is a directory")
            except NotADirectoryError:
                return ErrorArtifact("Not a directory")
            except Exception as e:
                return ErrorArtifact(f"Failed to load file: {str(e)}")

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
