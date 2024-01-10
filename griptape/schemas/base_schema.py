from __future__ import annotations
from types import UnionType
from typing import Union, get_origin, get_args
import attrs
from marshmallow import Schema, fields, pre_dump

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, list: fields.List, dict: fields.Dict, bytes: Bytes}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class."""
        from marshmallow import post_load

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                data = attrscls.before_load(data)

                return attrscls(**data)

            @pre_dump
            def transform(self, data, **kwargs):
                data = attrscls.before_dump(data)

                return data

        attrs.resolve_types(attrscls)
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

        allow_none = False
        if cls.is_union(type_):
            args = get_args(type_)
            origin_cls = args[0]
            if len(args) > 1 and args[1] is type(None):
                allow_none = True
        elif type_.__name__.startswith("Base"):
            return fields.Nested(PolymorphicSchema)
        elif attrs.has(type_):
            return fields.Nested(cls.from_attrscls(type_))
        else:
            origin_cls = get_origin(type_) or type_
        FieldClass = cls.DATACLASS_TYPE_MAPPING[origin_cls]
        required = default is None
        field_kwargs = {"required": required, "allow_none": allow_none, "cls_or_instance": None}
        # Handle list types
        if issubclass(FieldClass, fields.List):
            # Construct inner class
            args = get_args(type_)
            if args:
                inner_type = args[0]
                inner_field = cls.make_field_for_type(inner_type)
            else:
                inner_field = fields.Field()
            field_kwargs["cls_or_instance"] = inner_field
        return FieldClass(**field_kwargs)

    @classmethod
    def is_union(cls, t: object) -> bool:
        origin = get_origin(t)
        return origin is Union or origin is UnionType
