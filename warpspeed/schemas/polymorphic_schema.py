from pydoc import locate
from marshmallow import ValidationError
from marshmallow_oneofschema import OneOfSchema


class PolymorphicSchema(OneOfSchema):
    class SchemaGenerator:
        def get(self, key: str) -> object:
            klass = locate(f"warpspeed.schemas.{key}Schema")

            if klass:
                return klass
            else:
                raise ValidationError(f"Missing schema for '{key}'")

    @property
    def type_schemas(self) -> SchemaGenerator:
        return self.SchemaGenerator()
