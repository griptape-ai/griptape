import attrs
from marshmallow import Schema, fields


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, list: fields.List}

    @classmethod
    def from_attrscls(cls, attrscls):
        """Generate a Schema from an attrs class."""
        return cls.from_dict(
            {a.name: cls.make_field_for_type(a.type) for a in attrs.fields(attrscls)}, name=f"{attrscls.__name__}Schema"
        )

    @classmethod
    def make_field_for_type(cls, type_):
        """Generate a marshmallow Field instance from a Python type."""
        if attrs.has(type_):
            return fields.Nested(cls.from_attrscls(type_))
        # Get marshmallow field class for Python type
        origin_cls = getattr(type_, "__origin__", None) or type_
        FieldClass = cls.DATACLASS_TYPE_MAPPING[origin_cls]

        field_kwargs = {}

        # Handle list types
        if issubclass(FieldClass, fields.List):
            # Construct inner class
            args = getattr(type_, "__args__", [])
            if args:
                inner_type = args[0]
                inner_field = cls.make_field_for_type(inner_type)
            else:
                inner_field = fields.Field()
            field_kwargs["cls_or_instance"] = inner_field

        return FieldClass(**field_kwargs)
