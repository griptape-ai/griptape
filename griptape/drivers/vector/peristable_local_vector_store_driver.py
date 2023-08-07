import dataclasses
import json
from pathlib import Path
from typing import Union, Literal, cast, Dict
from zipfile import ZipFile

from attr import define, field

from griptape.drivers import LocalVectorStoreDriver


@define
class PersistableLocalVectorStoreDriver(LocalVectorStoreDriver):
    """
    Version of the LocalVectorStoreDriver that allows to serialize to a local file using either json or a zip
    depending on the suffix of the given file path.

    :param file_path: `pathlib.Path` or path as string. Name and location of the save file. Extension must be zip or
    json, if zip the generated file is compressed.
    """

    file_path: Union[Path, str] = field(kw_only=True, converter=Path)
    file_is_zip: bool = field(init=False)

    @classmethod
    def from_saved(cls, file_path) -> "PersistableLocalVectorStoreDriver":
        """Named Constructor that initialises an instance from a serialized one"""
        instance = cls(file_path=file_path)
        instance.load()
        return instance

    @file_path.validator
    def _check_file_path(self, attribute, value):
        if value.suffix not in (".json", ".zip"):
            raise ValueError(
                f"file must either be a json or a zip but file name is {self.file_path}"
            )

    def __attrs_post_init__(self):
        self.file_is_zip = self.file_path.suffix == ".zip"

    class _EntryAwareJSONEncoder(json.JSONEncoder):
        """Internal JSON encoder class that enables json serialization of `LocalVectorStore`s internal Entry structure."""

        def default(self, o):
            if isinstance(o, PersistableLocalVectorStoreDriver.Entry):
                d_dict = dataclasses.asdict(o)
                d_dict["__Entry__"] = True
                return d_dict
            return super().default(o)

        @staticmethod
        def json_deserialize_vector_store_entry(dct: Dict):
            """Deserialization hook"""

            if "__Entry__" in dct:
                dct.pop("__Entry__")
                return PersistableLocalVectorStoreDriver.Entry(**dct)

            return dct

    def store(self, overwrite=False):
        """Serialize the entries of the vectorstore. Will not overwrite an existing file unless overwrite=True"""

        write_mode = cast(Literal["w", "x"], "w" if overwrite else "x")

        if self.file_is_zip:
            with ZipFile(self.file_path, write_mode) as z_f:
                json_data = json.dumps(self.entries, cls=self._EntryAwareJSONEncoder)
                z_f.writestr("data.json", json_data)
        else:
            with open(self.file_path, write_mode) as f:
                json.dump(self.entries, f, cls=self._EntryAwareJSONEncoder)

    def load(self) -> None:
        """Read entries that have been serialized, automatically recognizes zipped saves by suffix.
        Will overwrite internal entries with the loaded ones"""
        if self.file_is_zip:
            with ZipFile(self.file_path) as zf:
                json_data = zf.read("data.json")
                self.entries = json.loads(
                    json_data,
                    object_hook=self._EntryAwareJSONEncoder.json_deserialize_vector_store_entry,
                )

        else:
            with open(self.file_path, "r") as f:
                self.entries = json.load(
                    f,
                    object_hook=self._EntryAwareJSONEncoder.json_deserialize_vector_store_entry,
                )


