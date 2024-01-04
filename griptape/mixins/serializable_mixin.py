from __future__ import annotations

import json
from importlib import import_module
from typing import TypeVar

from attr import Factory, define, field
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError

T = TypeVar("T", bound="SerializableMixin")


@define(slots=False)
class SerializableMixin:
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        class_name = data["type"]
        schema_class = SerializableMixin._import_schema_class(class_name)
        class_registry.register(class_name, schema_class)

        try:
            return class_registry.get_class(class_name)().load(data)  # pyright: ignore
        except RegistryError:
            raise ValueError("Unsupported type.")

    @classmethod
    def from_json(cls: type[T], data: str) -> T:
        return cls.from_dict(json.loads(data))

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        schema_class = SerializableMixin._import_schema_class(self.type)

        return dict(schema_class().dump(self))

    @classmethod
    def _import_schema_class(cls, class_name):
        schema_class_name = f"{class_name}Schema"
        schema_class = import_module(schema_class_name, "griptape.schemas").__getattribute__(schema_class_name)

        return schema_class
