from __future__ import annotations
import os
from pathlib import Path
from attr import define, field, Factory
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BaseArtifact, TextArtifact
from .base_file_manager_driver import BaseFileManagerDriver


@define
class LocalFileManagerDriver(BaseFileManagerDriver):
    """
    LocalFileManagerDriver can be used to list, load, and save files on the local file system.

    Attributes:
        workdir: The absolute working directory. List, load, and save operations will be performed relative to this directory.
    """

    workdir: str = field(default=Factory(lambda: os.getcwd()), kw_only=True)

    @workdir.validator  # pyright: ignore
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("Workdir must be an absolute path")

    def list_files(self, path: str) -> TextArtifact | ErrorArtifact:
        full_path = self._to_full_path(path)

        try:
            entries = os.listdir(full_path)
            return TextArtifact("\n".join([e for e in entries]))
        except FileNotFoundError:
            return ErrorArtifact("Path not found")
        except NotADirectoryError:
            return ErrorArtifact("Path is not a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to list files: {str(e)}")

    def _to_full_path(self, path: str) -> Path:
        path = path.lstrip("/")
        return Path(os.path.normpath(os.path.join(self.workdir, path)))

    def load_file(self, path: str) -> BaseArtifact:
        full_path = self._to_full_path(path)
        extension = path.split(".")[-1]
        loader = self.loaders.get(extension) or self.default_loader

        try:
            with open(full_path, "rb") as file:
                value = file.read()
            result = loader.load(value)
        except FileNotFoundError:
            return ErrorArtifact("Path not found")
        except IsADirectoryError:
            return ErrorArtifact("Path is a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to load file: {str(e)}")

        if isinstance(result, BaseArtifact):
            return result
        else:
            return ListArtifact(result)

    def save_file(self, path: str, value: bytes | str) -> InfoArtifact | ErrorArtifact:
        full_path = self._to_full_path(path)
        extension = path.split(".")[-1]
        loader = self.loaders.get(extension) or self.default_loader
        encoding = None if loader is None else loader.encoding

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            if isinstance(value, str):
                if encoding is None:
                    value = value.encode()
                else:
                    value = value.encode(encoding=encoding)
            elif isinstance(value, bytearray) or isinstance(value, memoryview):
                raise ValueError(f"Unsupported type: {type(value)}")

            with open(full_path, "wb") as file:
                file.write(value)
        except Exception as e:
            return ErrorArtifact(f"Failed to save file: {str(e)}")

        return InfoArtifact("Successfully saved file")
