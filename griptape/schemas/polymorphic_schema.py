from abc import abstractmethod
from pydoc import locate
from typing import Optional
from marshmallow import ValidationError, Schema
from griptape.schemas import BaseSchema


class PolymorphicSchema(BaseSchema):
    """
    PolymorphicSchema is based on https://github.com/marshmallow-code/marshmallow-oneofschema
    """

    def get_schema(self, class_name: str, obj: Optional[object], schema_namespace: Optional[str]):
        if schema_namespace:
            namespace = schema_namespace
        elif obj is not None and hasattr(obj, "schema_namespace"):
            if locate(f"griptape.schemas.{class_name}Schema"):
                namespace = "griptape.schemas"
            elif obj.schema_namespace is None:
                namespace = obj.schema_namespace = f"{obj.__module__}_schema"
            else:
                namespace = obj.schema_namespace
        else:
            namespace = "griptape.schemas"

        klass = locate(f"{namespace}.{class_name}Schema")

        if klass:
            return klass
        else:
            raise ValidationError(f"Missing schema for '{class_name}'")

    type_field = "type"
    type_field_remove = True

    def get_obj_type(self, obj):
        """Returns name of the schema during dump() calls, given the object
        being dumped."""
        return obj.__class__.__name__

    def get_data_type(self, data):
        """Returns name of the schema during load() calls, given the data being
        loaded. Defaults to looking up `type_field` in the data."""
        data_type = data.get(self.type_field)
        if self.type_field in data and self.type_field_remove:
            data.pop(self.type_field)
        return data_type

    def dump(self, obj, *, many=None, **kwargs):
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
            exc = ValidationError(errors, data=obj, valid_data=result)
            raise exc

    def _dump(self, obj, *, update_fields=True, **kwargs):
        obj_type = self.get_obj_type(obj)

        if not obj_type:
            return (None, {"_schema": "Unknown object class: %s" % obj.__class__.__name__})

        type_schema = self.get_schema(obj_type, obj, None)

        if not type_schema:
            return None, {"_schema": "Unsupported object type: %s" % obj_type}

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        result = schema.dump(obj, many=False, **kwargs)

        if result is not None:
            result[self.type_field] = obj_type

        return result

    def load(self, data, *, many=None, partial=None, unknown=None, **kwargs):
        errors = {}
        result_data = []
        result_errors = {}
        many = self.many if many is None else bool(many)
        if partial is None:
            partial = self.partial
        if not many:
            try:
                result = result_data = self._load(data, partial=partial, unknown=unknown, **kwargs)
                #  result_data.append(result)
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

    def _load(self, data, *, partial=None, unknown=None, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError({"_schema": "Invalid data type: %s" % data})

        data = dict(data)
        unknown = unknown or self.unknown
        data_type = self.get_data_type(data)

        if data_type is None:
            raise ValidationError({self.type_field: ["Missing data for required field."]})

        schema_namespace = data.get("schema_namespace")

        try:
            type_schema = self.get_schema(data_type, None, schema_namespace)
        except TypeError:
            # data_type could be unhashable
            raise ValidationError({self.type_field: ["Invalid value: %s" % data_type]})
        if not type_schema:
            raise ValidationError({self.type_field: ["Unsupported value: %s" % data_type]})

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        return schema.load(data, many=False, partial=partial, unknown=unknown, **kwargs)

    def validate(self, data, *, many=None, partial=None):
        try:
            self.load(data, many=many, partial=partial)
        except ValidationError as ve:
            return ve.messages
        return {}
