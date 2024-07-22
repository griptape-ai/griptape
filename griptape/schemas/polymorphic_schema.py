from typing import Any

from marshmallow import Schema, ValidationError

from griptape.schemas import BaseSchema


class PolymorphicSchema(BaseSchema):
    """PolymorphicSchema is based on https://github.com/marshmallow-code/marshmallow-oneofschema."""

    def __init__(self, inner_class: Any, **kwargs) -> None:
        super().__init__(**kwargs)

        self.inner_class = inner_class

    type_field = "type"
    type_field_remove = True

    def get_obj_type(self, obj: Any) -> Any:
        """Returns name of the schema during dump() calls, given the object being dumped."""
        return obj.__class__.__name__

    def get_data_type(self, data: Any) -> Any:
        """Returns name of the schema during load() calls, given the data being loaded. Defaults to looking up `type_field` in the data."""
        data_type = data.get(self.type_field)
        if self.type_field in data and self.type_field_remove:
            data.pop(self.type_field)
        return data_type

    def dump(self, obj: Any, *, many: Any = None, **kwargs) -> Any:
        errors = {}
        result_data = []
        result_errors = {}
        many = self.many if many is None else bool(many)
        if not many:
            result = result_data = self._dump(obj, **kwargs)
        else:
            for idx, o in enumerate(obj):
                try:
                    result = self._dump(o, **kwargs)
                    result_data.append(result)
                except ValidationError as error:
                    result_errors[idx] = error.normalized_messages()
                    result_data.append(error.valid_data)

        result = result_data
        errors = result_errors

        if not errors:
            return result
        else:
            exc = ValidationError(errors, data=obj, valid_data=result)  # pyright: ignore[reportArgumentType]
            raise exc

    def _dump(self, obj: Any, *, update_fields: bool = True, **kwargs) -> Any:
        obj_type = self.get_obj_type(obj)

        if not obj_type:
            return (None, {"_schema": f"Unknown object class: {obj.__class__.__name__}"})

        type_schema = BaseSchema.from_attrs_cls(obj.__class__)

        if not type_schema:
            return None, {"_schema": f"Unsupported object type: {obj_type}"}

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        result = schema.dump(obj, many=False, **kwargs)

        if result is not None:
            result[self.type_field] = obj_type  # pyright: ignore[reportArgumentType,reportCallIssue]

        return result

    def load(self, data: Any, *, many: Any = None, partial: Any = None, unknown: Any = None, **kwargs) -> Any:
        errors = {}
        result_data = []
        result_errors = {}
        many = self.many if many is None else bool(many)
        if partial is None:
            partial = self.partial
        if not many:
            try:
                result = result_data = self._load(data, partial=partial, unknown=unknown, **kwargs)
            except ValidationError as error:
                result_errors = error.normalized_messages()
                result_data.append(error.valid_data)
        else:
            for idx, item in enumerate(data):
                try:
                    result = self._load(item, partial=partial, **kwargs)
                    result_data.append(result)
                except ValidationError as error:
                    result_errors[idx] = error.normalized_messages()
                    result_data.append(error.valid_data)

        result = result_data
        errors = result_errors

        if not errors:
            return result
        else:
            exc = ValidationError(errors, data=data, valid_data=result)
            raise exc

    def _load(self, data: Any, *, partial: Any = None, unknown: Any = None, **kwargs) -> Any:
        if not isinstance(data, dict):
            raise ValidationError({"_schema": f"Invalid data type: {data}"})

        data = dict(data)
        unknown = unknown or self.unknown
        data_type = self.get_data_type(data)

        if data_type is None:
            raise ValidationError({self.type_field: ["Missing data for required field."]})

        type_schema = self.inner_class.get_schema(data_type)
        if not type_schema:
            raise ValidationError({self.type_field: [f"Unsupported value: {data_type}"]})

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        return schema.load(data, many=False, partial=partial, unknown=unknown, **kwargs)

    def validate(self, data: Any, *, many: Any = None, partial: Any = None) -> Any:  # pyright: ignore[reportIncompatibleMethodOverride]
        try:
            self.load(data, many=many, partial=partial)
        except ValidationError as ve:
            return ve.messages
        return {}
