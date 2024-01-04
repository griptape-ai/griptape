from __future__ import annotations
import builtins
import attrs
from marshmallow import Schema, fields


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, list: fields.List}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class."""
        return cls.from_dict(
            {a.name: cls.make_field_for_type(a.type) for a in attrs.fields(attrscls) if a.metadata.get("save")},
            name=f"{attrscls.__name__}Schema",
        )

    @classmethod
    def make_field_for_type(cls, type_str):
        """Generate a marshmallow Field instance from a Python type."""
        if attrs.has(type_str):
            return fields.Nested(cls.from_attrscls(type_str))
        type_info = cls.str_to_type(type_str)
        type_ = type_info["type"]
        field_class = Schema.TYPE_MAPPING[type_]

        field_kwargs = {"allow_none": type_info["optional"]}

        # Handle list types
        if issubclass(field_class, fields.List):
            # Construct inner class
            args = getattr(type_, "__args__", [])
            if args:
                inner_type = args[0]
                inner_field = cls.make_field_for_type(inner_type)
            else:
                inner_field = fields.Field()
            field_kwargs["cls_or_instance"] = inner_field

        return field_class(**field_kwargs)

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
