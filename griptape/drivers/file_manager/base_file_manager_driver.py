from __future__ import annotations

from abc import ABC, abstractmethod

from attrs import Factory, define, field

import griptape.loaders as loaders
from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact


@define
class BaseFileManagerDriver(ABC):
    """BaseFileManagerDriver can be used to list, load, and save files.

    Attributes:
        default_loader: The default loader to use for loading file contents into artifacts.
        loaders: Dictionary of file extension specific loaders to use for loading file contents into artifacts.
    """

    default_loader: loaders.BaseLoader = field(default=Factory(lambda: loaders.BlobLoader()), kw_only=True)
    loaders: dict[str, loaders.BaseLoader] = field(
        default=Factory(
            lambda: {
                "pdf": loaders.PdfLoader(),
                "csv": loaders.CsvLoader(),
                "txt": loaders.TextLoader(),
                "html": loaders.TextLoader(),
                "json": loaders.TextLoader(),
                "yaml": loaders.TextLoader(),
                "xml": loaders.TextLoader(),
                "png": loaders.ImageLoader(),
                "jpg": loaders.ImageLoader(),
                "jpeg": loaders.ImageLoader(),
                "webp": loaders.ImageLoader(),
                "gif": loaders.ImageLoader(),
                "bmp": loaders.ImageLoader(),
                "tiff": loaders.ImageLoader(),
            },
        ),
        kw_only=True,
    )

    def list_files(self, path: str) -> TextArtifact | ErrorArtifact:
        try:
            entries = self.try_list_files(path)
            return TextArtifact("\n".join(list(entries)))
        except FileNotFoundError:
            return ErrorArtifact("Path not found")
        except NotADirectoryError:
            return ErrorArtifact("Path is not a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to list files: {str(e)}")

    @abstractmethod
    def try_list_files(self, path: str) -> list[str]: ...

    def load_file(self, path: str) -> BaseArtifact:
        try:
            extension = path.split(".")[-1]
            loader = self.loaders.get(extension) or self.default_loader
            source = self.try_load_file(path)
            result = loader.load(source)

            if isinstance(result, BaseArtifact):
                return result
            else:
                return ListArtifact(result)
        except FileNotFoundError:
            return ErrorArtifact("Path not found")
        except IsADirectoryError:
            return ErrorArtifact("Path is a directory")
        except NotADirectoryError:
            return ErrorArtifact("Not a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to load file: {str(e)}")

    @abstractmethod
    def try_load_file(self, path: str) -> bytes: ...

    def save_file(self, path: str, value: bytes | str) -> InfoArtifact | ErrorArtifact:
        try:
            extension = path.split(".")[-1]
            loader = self.loaders.get(extension) or self.default_loader
            encoding = None if loader is None else loader.encoding

            if isinstance(value, str):
                value = value.encode() if encoding is None else value.encode(encoding=encoding)
            elif isinstance(value, (bytearray, memoryview)):
                raise ValueError(f"Unsupported type: {type(value)}")

            self.try_save_file(path, value)

            return InfoArtifact("Successfully saved file")
        except IsADirectoryError:
            return ErrorArtifact("Path is a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to save file: {str(e)}")

    @abstractmethod
    def try_save_file(self, path: str, value: bytes) -> None: ...
