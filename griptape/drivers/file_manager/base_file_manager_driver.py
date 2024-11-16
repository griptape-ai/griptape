from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact, BlobArtifact, InfoArtifact, TextArtifact


@define
class BaseFileManagerDriver(ABC):
    """BaseFileManagerDriver can be used to list, load, and save files.

    Attributes:
        default_loader: The default loader to use for loading file contents into artifacts.
        loaders: Dictionary of file extension specific loaders to use for loading file contents into artifacts.
    """

    _workdir: str = field(kw_only=True, alias="workdir")
    encoding: Optional[str] = field(default=None, kw_only=True)

    @property
    @abstractmethod
    def workdir(self) -> str: ...

    @workdir.setter
    @abstractmethod
    def workdir(self, value: str) -> None: ...

    def list_files(self, path: str) -> TextArtifact:
        entries = self.try_list_files(path)
        return TextArtifact("\n".join(list(entries)))

    @abstractmethod
    def try_list_files(self, path: str) -> list[str]: ...

    def load_file(self, path: str) -> BlobArtifact | TextArtifact:
        if self.encoding is None:
            return BlobArtifact(self.try_load_file(path))
        else:
            return TextArtifact(self.try_load_file(path).decode(encoding=self.encoding), encoding=self.encoding)

    @abstractmethod
    def try_load_file(self, path: str) -> bytes: ...

    def save_file(self, path: str, value: bytes | str) -> InfoArtifact:
        if isinstance(value, str):
            value = value.encode() if self.encoding is None else value.encode(encoding=self.encoding)
        elif isinstance(value, (bytearray, memoryview)):
            raise ValueError(f"Unsupported type: {type(value)}")

        location = self.try_save_file(path, value)

        return InfoArtifact(f"Successfully saved file at: {location}")

    @abstractmethod
    def try_save_file(self, path: str, value: bytes) -> str: ...

    def load_artifact(self, path: str) -> BaseArtifact:
        response = self.try_load_file(path)
        return BaseArtifact.from_json(
            response.decode() if self.encoding is None else response.decode(encoding=self.encoding)
        )

    def save_artifact(self, path: str, artifact: BaseArtifact) -> InfoArtifact:
        artifact_json = artifact.to_json()
        value = artifact_json.encode() if self.encoding is None else artifact_json.encode(encoding=self.encoding)

        location = self.try_save_file(path, value)

        return InfoArtifact(f"Successfully saved artifact at: {location}")
