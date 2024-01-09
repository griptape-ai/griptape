from __future__ import annotations
import builtins
from typing import Any
import attrs
from marshmallow import Schema, fields


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, list: fields.List}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class."""
        from marshmallow import post_load
        from importlib import import_module

        class SubSchema(cls):
            @post_load
            def make_obj(self, data, **kwargs):
                package_name = ".".join(attrscls.__module__.split(".")[:2])

                if "type" in data:
                    class_name = data["type"]

                    class_ = import_module(package_name).__getattribute__(class_name)

                    return class_(**data)
                else:
                    raise ValueError("Missing type field in schema.")

        return SubSchema.from_dict(
            {a.name: cls.make_field_for_type(a.type) for a in attrs.fields(attrscls) if a.metadata.get("save")},
            name=f"{attrscls.__name__}Schema",
        )

    @classmethod
    def make_field_for_type(cls, type_: Any):
        """Generate a marshmallow Field instance from a Python type."""

        # Sometimes we get a string instead of a type so we need to resolve it
        if isinstance(type_, str):
            from griptape.drivers import BaseEmbeddingDriver

            try:
                local_scope = {"BaseEmbeddingDriver": BaseEmbeddingDriver}

                if type_ in local_scope:
                    type_ = local_scope[type_]
            except NameError as e:
                raise ValueError(f"Unknown type: {type_}") from e

        # Check if type_obj is a valid type for attrs
        if isinstance(type_, type) and attrs.has(type_):
            return fields.Nested(cls.from_attrscls(type_))
        elif isinstance(type_, str):
            type_info = cls.str_to_type(type_)
            type_ = type_info["type"]
            field_class = Schema.TYPE_MAPPING[type_]

            field_kwargs = {"allow_none": type_info["optional"]}

            return field_class(**field_kwargs)
        else:
            raise ValueError(f"Unknown type: {type_}")

    @classmethod
    def str_to_type(cls, type_str: str) -> dict:
        # Split the string by the pipe symbol and strip whitespace
        types = [t.strip() for t in type_str.split("|")]

        type_info = {"type": None, "optional": False}
        for t in types:
            if t == "None":  # Special case for None
                type_info["optional"] = True
            elif hasattr(builtins, t):
                type_info["type"] = getattr(builtins, t)
            else:
                raise ValueError(f"Unknown type: {t}")

        return type_info
