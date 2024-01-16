from __future__ import annotations

from abc import ABC
from typing import Any, Union, get_args, get_origin

import attrs
from marshmallow import Schema, fields

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, dict: fields.Dict, bytes: Bytes}

    @classmethod
    def from_attrs_cls(cls, attrs_cls: type):
        """Generate a Schema from an attrs class.

        Args:
            attrs_cls: An attrs class.
        """
        from marshmallow import post_load

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                return attrs_cls(**data)

        cls._resolve_types(attrs_cls)
        return SubSchema.from_dict(
            {
                a.name: cls._get_field_for_type(a.type)
                for a in attrs.fields(attrs_cls)
                if a.metadata.get("serializable")
            },
            name=f"{attrs_cls.__name__}Schema",
        )

    @classmethod
    def _get_field_for_type(cls, field_type: type):
        """Generate a marshmallow Field instance from a Python type.

        Args:
            field_type: An variable type.
        """
        from griptape.schemas.polymorphic_schema import PolymorphicSchema

        field_kwargs: dict[str, Any] = {"allow_none": False}

        field_class, args = cls._get_field_class(field_type)

        if attrs.has(field_class):
            if issubclass(field_class, ABC):
                return fields.Nested(PolymorphicSchema(inner_class=field_class))
            else:
                return fields.Nested(cls.from_attrs_cls(field_type))
        elif issubclass(field_class, list):
            return fields.List(cls_or_instance=cls._get_field_for_type(args[0]))
        else:
            FieldClass = cls.DATACLASS_TYPE_MAPPING[field_class]
            if len(args) > 1 and args[1] is type(None):
                field_kwargs["allow_none"] = True

            return FieldClass(**field_kwargs)

    @classmethod
    def _get_field_class(cls, field_type: type):
        origin = get_origin(field_type) or field_type

        if origin is Union:
            args = get_args(field_type)
            field_class = args[0]

        else:
            args = get_args(field_type)
            field_class = origin

        return field_class, args

    @classmethod
    def _resolve_types(cls, attrs_cls: type):
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
