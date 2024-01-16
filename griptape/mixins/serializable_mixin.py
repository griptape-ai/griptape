from __future__ import annotations

import json
from typing import TypeVar, Generic, cast

from attr import Factory, define, field
from abc import ABC

from marshmallow import Schema
from griptape.schemas.base_schema import BaseSchema
from importlib import import_module

T = TypeVar("T", bound="SerializableMixin")


@define(slots=False)
class SerializableMixin(Generic[T]):
    type: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )

    @classmethod
    def get_schema(cls: type[T], obj_type: str) -> Schema:
        if issubclass(cls, ABC):
            package_name = ".".join(cls.__module__.split(".")[:-1])
            module = getattr(import_module(package_name), obj_type, None)

            if module is None:
                raise ValueError(f"Could not find module: {package_name}.{obj_type}")

            schema_class = BaseSchema.from_attrs_cls(module)
        else:
            schema_class = BaseSchema.from_attrs_cls(cls)

        return schema_class()

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        if "type" in data:
            return cast(T, cls.get_schema(data["type"]).load(data))
        else:
            raise ValueError(f"Missing type field in data: {data}")

    @classmethod
    def from_json(cls: type[T], data: str) -> T:
        return cls.from_dict(json.loads(data))

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        schema = BaseSchema.from_attrs_cls(self.__class__)

        return dict(schema().dump(self))
