from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from attr import Factory, define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact, InfoArtifact
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

    @abstractmethod
    def list_files(self, path: str) -> TextArtifact | ErrorArtifact:
        ...

    @abstractmethod
    def load_file(self, path: str) -> BaseArtifact:
        ...

    @abstractmethod
    def save_file(self, path: str, value: bytes | str) -> InfoArtifact | ErrorArtifact:
        ...
