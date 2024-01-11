from __future__ import annotations
import sys
from abc import ABC
from typing import Union, get_origin, get_args, Any
import attrs
from marshmallow import Schema, fields

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, dict: fields.Dict, bytes: Bytes}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class.

        Args:
            attrscls: An attrs class.
        """

        from marshmallow import post_load
        from griptape.utils import PromptStack
        from griptape.structures import Structure
        from griptape.drivers import BaseConversationMemoryDriver, BasePromptDriver

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                return attrscls(**data)

        attrs.resolve_types(
            attrscls,
            localns={
                "PromptStack": PromptStack,
                "Input": PromptStack.Input,
                "Structure": Structure,
                "BaseConversationMemoryDriver": BaseConversationMemoryDriver,
                "BasePromptDriver": BasePromptDriver,
            },
        )
        return SubSchema.from_dict(
            {
                a.name: cls.make_field_for_type(a.type, a.default)
                for a in attrs.fields(attrscls)
                if a.metadata.get("serialize")
            },
            name=f"{attrscls.__name__}Schema",
        )

    @classmethod
    def make_field_for_type(cls, type_: type, default=None):
        """Generate a marshmallow Field instance from a Python type."""
        from griptape.schemas.polymorphic_schema import PolymorphicSchema

        field_kwargs: dict[str, Any] = {"allow_none": False}

        if cls.is_union(type_):
            args = get_args(type_)
            field_class = args[0]

            if len(args) > 1 and args[1] is type(None):
                field_kwargs["allow_none"] = True
        else:
            args = get_args(type_)
            field_class = get_origin(type_) or type_

        if attrs.has(field_class):
            if issubclass(field_class, ABC):
                return fields.Nested(PolymorphicSchema(inner_class=field_class))
            else:
                return fields.Nested(cls.from_attrscls(type_))
        elif issubclass(field_class, list):
            return fields.List(cls_or_instance=cls.make_field_for_type(args[0]))
        else:
            FieldClass = cls.DATACLASS_TYPE_MAPPING[field_class]

            return FieldClass(**field_kwargs)

    @classmethod
    def is_union(cls, t: object) -> bool:
        origin = get_origin(t)

        if sys.version_info >= (3, 10):
            from types import UnionType

            return origin is Union or origin is UnionType
        else:
            return origin is Union
