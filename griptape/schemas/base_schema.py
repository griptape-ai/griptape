from __future__ import annotations
from types import UnionType
from typing import Union, get_origin, get_args, Any
import attrs
from marshmallow import Schema, fields, pre_dump

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, dict: fields.Dict, bytes: Bytes}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class."""
        from marshmallow import post_load

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                if hasattr(attrscls, "before_load"):
                    data = attrscls.before_load(data)

                return attrscls(**data)

            @pre_dump
            def transform(self, data, **kwargs):
                if hasattr(data, "before_dump"):
                    data = attrscls.before_dump(data)

                return data

        from griptape.utils import PromptStack
        from griptape.structures import Structure
        from griptape.drivers import BaseConversationMemoryDriver

        attrs.resolve_types(
            attrscls,
            localns={
                "PromptStack": PromptStack,
                "Input": PromptStack.Input,
                "Structure": Structure,
                "BaseConversationMemoryDriver": BaseConversationMemoryDriver,
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

        if field_class.__name__.startswith("Base"):
            return fields.Nested(PolymorphicSchema(class_=field_class))
        elif attrs.has(field_class):
            return fields.Nested(cls.from_attrscls(type_))
        elif issubclass(field_class, list):
            return fields.List(cls_or_instance=cls.make_field_for_type(args[0]))
        else:
            FieldClass = cls.DATACLASS_TYPE_MAPPING[field_class]
            return FieldClass(**field_kwargs)

    @classmethod
    def is_union(cls, t: object) -> bool:
        origin = get_origin(t)
        return origin is Union or origin is UnionType
