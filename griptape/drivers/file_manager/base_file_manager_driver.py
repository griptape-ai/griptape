from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from attr import Factory, define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact, InfoArtifact, ListArtifact
from griptape.loaders import BaseLoader, CsvLoader, ImageLoader, PdfLoader, TextLoader


@define
class BaseFileManagerDriver(ABC):
    """
    BaseFileManagerDriver can be used to list, load, and save files.

    Attributes:
        default_loader: The default loader to use for loading file contents into artifacts.
        loaders: Dictionary of file extension specifc loaders to use for loading file contents into artifacts.
    """

    default_loader: Optional[BaseLoader] = field(default=None, kw_only=True)
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
                "png": ImageLoader(),
                "jpg": ImageLoader(),
                "jpeg": ImageLoader(),
                "webp": ImageLoader(),
                "gif": ImageLoader(),
                "bmp": ImageLoader(),
                "tiff": ImageLoader(),
            }
        ),
        kw_only=True,
    )

    def list_files(self, path: str) -> TextArtifact | ErrorArtifact:
        try:
            entries = self.try_list_files(path)
            return TextArtifact("\n".join([e for e in entries]))
        except FileNotFoundError:
            return ErrorArtifact("Path not found")
        except NotADirectoryError:
            return ErrorArtifact("Path is not a directory")
        except Exception as e:
            return ErrorArtifact(f"Failed to list files: {str(e)}")

    @abstractmethod
    def try_list_files(self, path: str) -> list[str]:
        ...

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
        except Exception as e:
            return ErrorArtifact(f"Failed to load file: {str(e)}")

    @abstractmethod
    def try_load_file(self, path: str) -> bytes:
        ...

    def save_file(self, path: str, value: bytes | str) -> InfoArtifact | ErrorArtifact:
        try:
            extension = path.split(".")[-1]
            loader = self.loaders.get(extension) or self.default_loader
            encoding = None if loader is None else loader.encoding

            if isinstance(value, str):
                if encoding is None:
                    value = value.encode()
                else:
                    value = value.encode(encoding=encoding)
            elif isinstance(value, bytearray) or isinstance(value, memoryview):
                raise ValueError(f"Unsupported type: {type(value)}")

            self.try_save_file(path, value)

            return InfoArtifact("Successfully saved file")
        except Exception as e:
            return ErrorArtifact(f"Failed to save file: {str(e)}")

    @abstractmethod
    def try_save_file(self, path: str, value: bytes):
        ...
