from __future__ import annotations

from typing import Any

import marshmallow
import marshmallow.error_store
import marshmallow.exceptions


class MarshmallowUnionError(Exception):
    """Base error for marshmallow_union."""


class ExceptionGroupError(MarshmallowUnionError):
    """Collection of possibly multiple exceptions."""

    def __init__(self, msg: str, errors: Any) -> None:
        self.msg = msg
        self.errors = errors
        super().__init__(msg, errors)


class Union(marshmallow.fields.Field):
    """Field that accepts any one of multiple fields.

    Source: https://github.com/adamboche/python-marshmallow-union
    Each argument will be tried until one succeeds.

    Args:
        fields: The list of candidate fields to try.
        reverse_serialize_candidates: Whether to try the candidates in reverse order when serializing.
    """

    def __init__(
        self,
        fields: list[marshmallow.fields.Field],
        *,
        reverse_serialize_candidates: bool = False,
        **kwargs: Any,
    ) -> None:
        self._candidate_fields = fields
        self._reverse_serialize_candidates = reverse_serialize_candidates
        super().__init__(**kwargs)

    def _serialize(self, value: Any, attr: str | None, obj: str, **kwargs: Any) -> Any:
        """Pulls the value for the given key from the object, applies the field's formatting and returns the result.

        Args:
            value: The value to be serialized.
            attr: The attribute or key to get from the object.
            obj: The object to pull the key from.
            kwargs: Field-specific keyword arguments.

        Raises:
            marshmallow.exceptions.ValidationError: In case of formatting problem
        """
        error_store = kwargs.pop("error_store", marshmallow.error_store.ErrorStore())
        fields = (
            list(reversed(self._candidate_fields)) if self._reverse_serialize_candidates else self._candidate_fields
        )

        for candidate_field in fields:
            try:
                # pylint: disable=protected-access
                return candidate_field._serialize(value, attr, obj, error_store=error_store, **kwargs)
            except (TypeError, ValueError) as e:
                error_store.store_error({attr: str(e)})

        raise ExceptionGroupError("All serializers raised exceptions.", error_store.errors)

    def _deserialize(self, value: Any, attr: str | None = None, data: Any = None, **kwargs: Any) -> Any:
        """Deserialize ``value``.

        Args:
            value: The value to be deserialized.
            attr: The attribute/key in `data` to be deserialized.
            data: The raw input data passed to the `Schema.load`.
            kwargs: Field-specific keyword arguments.

        Raises:
            ValidationError: If an invalid value is passed or if a required value is missing.
        """
        errors = []
        for candidate_field in self._candidate_fields:
            try:
                return candidate_field.deserialize(value, attr, data, **kwargs)
            except marshmallow.exceptions.ValidationError as exc:
                errors.append(exc.messages)

        raise marshmallow.exceptions.ValidationError(message=errors, field_name=attr or "")
