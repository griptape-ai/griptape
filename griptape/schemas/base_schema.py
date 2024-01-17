from __future__ import annotations

from abc import ABC
from typing import Union, get_args, get_origin
from collections.abc import Sequence

import attrs
from marshmallow import Schema, fields

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, dict: fields.Dict, bytes: Bytes}

    @classmethod
    def from_attrs_cls(cls, attrs_cls: type) -> type:
        """Generate a Schema from an attrs class.

        Args:
            attrs_cls: An attrs class.
        """
        from marshmallow import post_load
        from griptape.mixins import SerializableMixin

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                return attrs_cls(**data)

        if issubclass(attrs_cls, SerializableMixin):
            cls._resolve_types(attrs_cls)
            return SubSchema.from_dict(
                {
                    a.name: cls._get_field_for_type(a.type)
                    for a in attrs.fields(attrs_cls)
                    if a.metadata.get("serializable")
                },
                name=f"{attrs_cls.__name__}Schema",
            )
        else:
            raise ValueError(f"Class must implement SerializableMixin: {attrs_cls}")

    @classmethod
    def _get_field_for_type(cls, field_type: type) -> fields.Field | fields.Nested:
        """Generate a marshmallow Field instance from a Python type.

        Args:
            field_type: A field type.
        """
        from griptape.schemas.polymorphic_schema import PolymorphicSchema

        field_class, args, optional = cls._get_field_type_info(field_type)

        if attrs.has(field_class):
            if ABC in field_class.__bases__:
                return fields.Nested(PolymorphicSchema(inner_class=field_class))
            else:
                return fields.Nested(cls.from_attrs_cls(field_type))
        elif cls.is_list_sequence(field_class):
            if args:
                return fields.List(cls_or_instance=cls._get_field_for_type(args[0]))
            else:
                raise ValueError(f"Missing type for list field: {field_type}")
        else:
            FieldClass = cls.DATACLASS_TYPE_MAPPING[field_class]

            return FieldClass(**{"allow_none": optional})

    @classmethod
    def _get_field_type_info(cls, field_type: type) -> tuple[type, tuple[type, ...], bool]:
        """Get information about a field type.

        Args:
            field_type: A field type.
        """
        origin = get_origin(field_type) or field_type
        args = get_args(field_type)
        optional = False

        if origin is Union:
            origin = args[0]
            if len(args) > 1 and args[1] is type(None):
                optional = True

            origin, args, _ = cls._get_field_type_info(origin)

        return origin, args, optional

    @classmethod
    def _resolve_types(cls, attrs_cls: type) -> None:
        """Resolve types in an attrs class.

        Args:
            attrs_cls: An attrs class.
        """

        # These modules are required to avoid `NameError`s when resolving types.
        from griptape.drivers import BaseConversationMemoryDriver, BasePromptDriver
        from griptape.structures import Structure
        from griptape.utils import PromptStack

        attrs.resolve_types(
            attrs_cls,
            localns={
                "PromptStack": PromptStack,
                "Input": PromptStack.Input,
                "Structure": Structure,
                "BaseConversationMemoryDriver": BaseConversationMemoryDriver,
                "BasePromptDriver": BasePromptDriver,
            },
        )

    @classmethod
    def is_list_sequence(cls, field_type: type) -> bool:
        if issubclass(field_type, str) or issubclass(field_type, bytes) or issubclass(field_type, tuple):
            return False
        else:
            return issubclass(field_type, Sequence)
