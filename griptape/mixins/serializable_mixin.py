from __future__ import annotations

import json
from abc import ABC
from importlib import import_module
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, cast

from attrs import Factory, define, field

from griptape.schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from marshmallow import Schema

T = TypeVar("T", bound="SerializableMixin")


def _default(_self: Any, obj: Any) -> Any:
    """Fallback method for JSONEncoder to handle custom serialization."""
    return getattr(obj.__class__, "to_dict", getattr(_default, "default"))(obj)


# Adapted from https://stackoverflow.com/questions/18478287/making-object-json-serializable-with-regular-encoder/18561055#18561055
setattr(_default, "default", JSONEncoder.default)
setattr(JSONEncoder, "default", _default)


@define(slots=False)
class SerializableMixin(Generic[T]):
    type: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    module_name: str = field(
        default=Factory(lambda self: self.__class__.__module__, takes_self=True),
        kw_only=True,
        metadata={"serializable": False},
    )

    @classmethod
    def get_schema(
        cls: type[T],
        subclass_name: Optional[str] = None,
        *,
        module_name: Optional[str] = None,
        types_overrides: Optional[dict[str, type]] = None,
        serializable_overrides: Optional[dict[str, bool]] = None,
    ) -> Schema:
        """Generates a Marshmallow schema for the class.

        Args:
            subclass_name: An optional subclass name. Required if the class is abstract.
            module_name: An optional module name. Defaults to the class's module.
            types_overrides: An optional dictionary of field names to override type.
            serializable_overrides: An optional dictionary of field names to override serializable status.
        """
        if ABC in cls.__bases__:
            if subclass_name is None:
                raise ValueError(f"Type field is required for abstract class: {cls.__name__}")

            module_name = module_name or cls.__module__
            subclass_cls = cls._import_cls_rec(module_name, subclass_name)

            schema_class = BaseSchema.from_attrs_cls(
                subclass_cls, types_overrides=types_overrides, serializable_overrides=serializable_overrides
            )
        else:
            schema_class = BaseSchema.from_attrs_cls(
                cls, types_overrides=types_overrides, serializable_overrides=serializable_overrides
            )

        return schema_class()

    @classmethod
    def from_dict(
        cls: type[T],
        data: dict,
        *,
        types_overrides: Optional[dict[str, type]] = None,
        serializable_overrides: Optional[dict[str, bool]] = None,
    ) -> T:
        return cast(
            "T",
            cls.get_schema(
                subclass_name=data.get("type"),
                module_name=data.get("module_name"),
                types_overrides=types_overrides,
                serializable_overrides=serializable_overrides,
            ).load(data),
        )

    @classmethod
    def from_json(
        cls: type[T],
        data: str,
        *,
        types_overrides: Optional[dict[str, type]] = None,
        serializable_overrides: Optional[dict[str, bool]] = None,
    ) -> T:
        return cls.from_dict(
            json.loads(data), types_overrides=types_overrides, serializable_overrides=serializable_overrides
        )

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(
        self,
        *,
        types_overrides: Optional[dict[str, type]] = None,
        serializable_overrides: Optional[dict[str, bool]] = None,
    ) -> str:
        return json.dumps(self.to_dict(types_overrides=types_overrides, serializable_overrides=serializable_overrides))

    def to_dict(
        self,
        *,
        types_overrides: Optional[dict[str, type]] = None,
        serializable_overrides: Optional[dict[str, bool]] = None,
    ) -> dict:
        schema = BaseSchema.from_attrs_cls(
            self.__class__, types_overrides=types_overrides, serializable_overrides=serializable_overrides
        )

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
        return test
