from __future__ import annotations

import json
from typing import TypeVar, Generic, cast

from attr import Factory, define, field

from marshmallow import class_registry, Schema
from marshmallow.exceptions import RegistryError
from griptape.schemas.base_schema import BaseSchema

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
        schema_class = cls.try_get_schema(obj_type)

        if isinstance(schema_class, type):
            return schema_class()
        else:
            raise RegistryError(f"Unsupported type: {obj_type}")

    @classmethod
    def try_get_schema(cls: type[T], obj_type: str) -> list[type[Schema]] | type[Schema]:
        class_registry.register(obj_type, BaseSchema.from_attrs_cls(cls))

        return class_registry.get_class(obj_type)

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
