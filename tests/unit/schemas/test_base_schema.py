from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

import pytest
from marshmallow import fields

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.loaders import TextLoader
from griptape.schemas import PolymorphicSchema
from griptape.schemas.base_schema import BaseSchema
from griptape.schemas.bytes_field import Bytes
from griptape.schemas.union_field import UnionField
from tests.mocks.mock_serializable import MockSerializable


class TestBaseSchema:
    def test_from_attrs_cls(self):
        schema = BaseSchema.from_attrs_cls(MockSerializable)()
        assert isinstance(schema, BaseSchema)

        assert isinstance(schema.fields["foo"], fields.Str)
        # Check if "bar" is a String that allows None (Optional)
        assert isinstance(schema.fields["bar"], UnionField)
        assert isinstance(schema.fields["bar"]._candidate_fields[0], fields.Str)
        assert schema.fields["bar"].allow_none is True

        assert isinstance(schema.fields["baz"], UnionField)
        assert isinstance(schema.fields["baz"]._candidate_fields[0], fields.List)
        assert isinstance(schema.fields["baz"]._candidate_fields[0].inner, fields.Integer)
        assert schema.fields["baz"].allow_none is True

        with pytest.raises(ValueError):
            BaseSchema.from_attrs_cls(TextLoader)

    def test_get_field_for_type(self):
        assert isinstance(BaseSchema._get_field_for_type(BaseArtifact), fields.Nested)

        # Base class should be a polymorphic schema
        field = BaseSchema._get_field_for_type(BaseArtifact)
        assert isinstance(field, fields.Nested)
        assert isinstance(field.nested, PolymorphicSchema)
        # Subclass should be nested schemas
        assert isinstance(BaseSchema._get_field_for_type(TextArtifact), fields.Nested)

        assert isinstance(BaseSchema._get_field_for_type(list[str]), fields.List)

        assert isinstance(BaseSchema._get_field_for_type(str), fields.Str)
        assert isinstance(BaseSchema._get_field_for_type(bytes), Bytes)
        assert isinstance(BaseSchema._get_field_for_type(datetime), fields.DateTime)
        assert isinstance(BaseSchema._get_field_for_type(float), fields.Float)
        assert isinstance(BaseSchema._get_field_for_type(bool), fields.Bool)
        assert isinstance(BaseSchema._get_field_for_type(tuple), fields.Raw)
        assert isinstance(BaseSchema._get_field_for_type(dict), fields.Dict)
        with pytest.raises(ValueError):
            BaseSchema._get_field_for_type(list)

    def test_get_field_type_info(self):
        assert BaseSchema._get_field_type_info(str) == (str, (), False)
        assert BaseSchema._get_field_type_info(list[str]) == (list, (str,), False)

        assert BaseSchema._get_field_type_info(Optional[str]) == (str, (), True)
        assert BaseSchema._get_field_type_info(Optional[list[str]]) == (list, (str,), True)

        assert BaseSchema._get_field_type_info(Union[str, None]) == (str, (), True)
        assert BaseSchema._get_field_type_info(Union[list[str], None]) == (list, (str,), True)

        assert BaseSchema._get_field_type_info(Union[str, int]) == (str, (), False)

        assert BaseSchema._get_field_type_info(list) == (list, (), False)

        assert BaseSchema._get_field_type_info(Literal["foo"]) == (str, (), False)  # pyright: ignore[reportArgumentType]
        assert BaseSchema._get_field_type_info(Literal[5]) == (int, (), False)  # pyright: ignore[reportArgumentType]

    def test_is_list_sequence(self):
        assert BaseSchema.is_list_sequence(list)
        assert not BaseSchema.is_list_sequence(tuple)
        assert not BaseSchema.is_list_sequence(bytes)
        assert not BaseSchema.is_list_sequence(str)
        assert not BaseSchema.is_list_sequence(int)

    def test_load(self):
        schema = BaseSchema.from_attrs_cls(MockSerializable)()
        mock_serializable = schema.load({"foo": "baz", "bar": "qux", "baz": [1, 2, 3]})
        assert mock_serializable.foo == "baz"
        assert mock_serializable.bar == "qux"
        assert mock_serializable.baz == [1, 2, 3]

    def test_load_with_unknown_attribute(self):
        schema = BaseSchema.from_attrs_cls(MockSerializable)()
        with pytest.raises(TypeError):
            schema.load({"foo": "baz", "bar": "qux", "baz": [1, 2, 3], "zoop": "bop"})

    def test_handle_union_in_list(self):
        field = BaseSchema._get_field_for_type(list[Union[str, list[str]]])
        assert isinstance(field, fields.List)
        assert isinstance(field.inner, UnionField)

        union_field = field.inner
        assert isinstance(union_field, UnionField)

        # Check that the union contains both str and List of str fields
        candidate_fields = [type(f) for f in union_field._candidate_fields]
        assert fields.Str in candidate_fields
        assert fields.List in candidate_fields

    def test_handle_union_outside_list(self):
        # Test a Union of str and int
        field = BaseSchema._get_field_for_type(Union[str, int])
        assert isinstance(field, UnionField)

        # Check that the union contains both str and int fields
        candidate_fields = [type(f) for f in field._candidate_fields]
        assert fields.Str in candidate_fields
        assert fields.Integer in candidate_fields
