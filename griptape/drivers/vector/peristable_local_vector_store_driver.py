import pathlib
import pickle
from pathlib import Path
from typing import Union

from attr import define, field
from griptape.drivers import LocalVectorStoreDriver


@define
class PersistableLocalVectorStoreDriver(LocalVectorStoreDriver):
    """
    Version of the LocalVectorStoreDriver that allows to serialize to a local file using pickle.

    :param file_path: `pathlib.Path` or path as string. Intended location of the pickle.
    """

    file_path: Union[Path, str] = field(kw_only=True)

    def store(self, overwrite=False):
        """Serialize the entries of the vectorstore. Will not overwrite an existing file unless overwrite=True"""
        with open(self.file_path, "xb" if not overwrite else "wb") as f:
            pickle.dump(self.entries, f)

    def load(self) -> None:
        """Read entries that have been serialized using pickle. Will overwrite internal entries with the loaded ones"""
        with open(self.file_path, "rb") as f:
            self.entries = pickle.load(f)

    @classmethod
    def from_saved(cls, file_path) -> "PersistableLocalVectorStoreDriver":
        """Named Constructor that initialises an instance from a serialized one"""
        instance = cls(file_path=file_path)
        instance.load()
        return instance
