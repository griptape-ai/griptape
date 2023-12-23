from __future__ import annotations

import logging
import os
from pathlib import Path
from attr import define, field, Factory
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BaseArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.loaders import FileLoader, BaseLoader, PdfLoader, CsvLoader, TextLoader
from schema import Schema, Literal
from typing import Optional


@define
class FileManager(BaseTool):
    """
    FileManager is a tool that can be used to load and save files.

    Attributes:
        workdir: The absolute directory to load files from and save files to.
        loaders: Dictionary of file extensions and matching loaders to use when loading files in load_files_from_disk.
        default_loader: The loader to use when loading files in load_files_from_disk without any matching loader in `loaders`.
        save_file_encoding: The encoding to use when saving files to disk.
    """

    workdir: str = field(default=Factory(lambda: os.getcwd()), kw_only=True)
    default_loader: BaseLoader = field(default=Factory(lambda: FileLoader()))
    loaders: dict[str, BaseLoader] = field(
        default=Factory(
            lambda: {
                "pdf": PdfLoader(),
                "csv": CsvLoader(),
                "txt": TextLoader(),
                "html": TextLoader(),
                "json": TextLoader(),
                "yaml": TextLoader(),
                "xml": TextLoader(),
            }
        ),
        kw_only=True,
    )
    save_file_encoding: str | None = field(default=None, kw_only=True)

    @workdir.validator
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("workdir has to be absolute absolute")

    @activity(
        config={
            "description": "Can be used to load files from disk",
            "schema": Schema(
                {
                    Literal(
                        "paths",
                        description="Paths to files to be loaded in the POSIX format. For example, ['foo/bar/file.txt']",
                    ): []
                }
            ),
        }
    )
    def load_files_from_disk(self, params: dict) -> ListArtifact | ErrorArtifact:
        list_artifact = ListArtifact()

        for path in params["values"]["paths"]:
            full_path = Path(os.path.join(self.workdir, path))
            extension = path.split(".")[-1]
            loader = self.loaders.get(extension) or self.default_loader
            result = loader.load(full_path)

            if isinstance(result, list):
                list_artifact.value.extend(result)
            elif isinstance(result, BaseArtifact):
                list_artifact.value.append(result)
            else:
                logging.warning(f"Unknown loader return type for file {path}")

        return list_artifact

    @activity(
        config={
            "description": "Can be used to save memory artifacts to disk",
            "schema": Schema(
                {
                    Literal(
                        "dir_name",
                        description="Destination directory name on disk in the POSIX format. For example, 'foo/bar'",
                    ): str,
                    Literal("file_name", description="Destination file name. For example, 'baz.txt'"): str,
                    "memory_name": str,
                    "artifact_namespace": str,
                }
            ),
        }
    )
    def save_memory_artifacts_to_disk(self, params: dict) -> ErrorArtifact | InfoArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        dir_name = params["values"]["dir_name"]
        file_name = params["values"]["file_name"]

        if memory:
            list_artifact = memory.load_artifacts(artifact_namespace)

            if len(list_artifact) == 0:
                return ErrorArtifact("no artifacts found")
            elif len(list_artifact) == 1:
                try:
                    self._save_to_disk(os.path.join(self.workdir, dir_name, file_name), list_artifact.value[0].value)

                    return InfoArtifact(f"saved successfully")
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")
            else:
                try:
                    for a in list_artifact.value:
                        self._save_to_disk(os.path.join(self.workdir, dir_name, f"{a.name}-{file_name}"), a.to_text())

                    return InfoArtifact(f"saved successfully")
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")
        else:
            return ErrorArtifact("memory not found")

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
                }
            ),
        }
    )
    def save_content_to_file(self, params: dict) -> ErrorArtifact | InfoArtifact:
        content = params["values"]["content"]
        new_path = params["values"]["path"]
        full_path = os.path.join(self.workdir, new_path)

        try:
            self._save_to_disk(full_path, content)

            return InfoArtifact(f"saved successfully")
        except Exception as e:
            return ErrorArtifact(f"error writing file to disk: {e}")

    def _save_to_disk(self, path: str, value: any) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as file:
            if isinstance(value, str):
                if self.save_file_encoding:
                    file.write(value.encode(self.save_file_encoding))
                else:
                    file.write(value.encode())
            else:
                file.write(value)
