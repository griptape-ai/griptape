from __future__ import annotations

import json
from abc import ABC
from importlib import import_module
from typing import TYPE_CHECKING, Generic, Optional, TypeVar, cast

from attrs import Factory, define, field

from griptape.schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from marshmallow import Schema

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

            subclass_cls = cls._import_cls_rec(cls.__module__, subclass_name)

            schema_class = BaseSchema.from_attrs_cls(subclass_cls)
        else:
            schema_class = BaseSchema.from_attrs_cls(cls)

        return schema_class()

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        return cast(T, cls.get_schema(subclass_name=data.get("type")).load(data))

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

    @classmethod
    def _import_cls_rec(cls, module_name: str, class_name: str) -> type:
        """Imports a class given a module name and class name.

        Will recursively traverse up the module's path until it finds a
        package that it can import `class_name` from.

        Args:
            module_name: The module name.
            class_name: The class name.

        Returns:
            The imported class if found. Raises `ValueError` if not found.
        """
        try:
            module = import_module(module_name)
            test = getattr(module, class_name, None)
        except ModuleNotFoundError:
            test = None

        if test is None:
            module_dirs = module_name.split(".")[:-1]
            module_name = ".".join(module_dirs)

            if not len(module_dirs):
                raise ValueError(f"Unable to import class: {class_name}")
            return cls._import_cls_rec(module_name, class_name)
        else:
            return test
