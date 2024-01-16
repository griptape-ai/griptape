from __future__ import annotations

import json
from typing import TypeVar, Generic, cast, Optional

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
    def get_schema(cls: type[T], subclass_name: Optional[str] = None) -> Schema:
        """Generates a Marshmallow schema for the class.

        Args:
            subclass_name: An optional subclass name. Required if the class is abstract.
        """
        if ABC in cls.__bases__:
            if subclass_name is None:
                raise ValueError(f"Type field is required for abstract class: {cls.__name__}")

            package_name = ".".join(cls.__module__.split(".")[:-1])
            module = getattr(import_module(package_name), subclass_name, None)

            if module is None:
                raise ValueError(f"Could not find module: {package_name}.{subclass_name}")

            schema_class = BaseSchema.from_attrs_cls(module)
        else:
            schema_class = BaseSchema.from_attrs_cls(cls)

        return schema_class()

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        return cast(T, cls.get_schema(subclass_name=data["type"] if "type" in data else None).load(data))

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
