from __future__ import annotations
from datetime import datetime
import pytest
from typing import Union, Optional
from marshmallow import fields
from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.schemas import PolymorphicSchema
from griptape.schemas.bytes_field import Bytes
from griptape.schemas.base_schema import BaseSchema
from griptape.loaders import TextLoader
from tests.mocks.mock_serializable import MockSerializable


class TestBaseSchema:
    def test_from_attrs_cls(self):
        schema = BaseSchema.from_attrs_cls(MockSerializable)()
        assert isinstance(schema, BaseSchema)

        assert isinstance(schema.fields["foo"], fields.Str)
        assert isinstance(schema.fields["bar"], fields.Str)
        assert schema.fields["bar"].allow_none
        assert isinstance(schema.fields["baz"], fields.List)
        assert isinstance(schema.fields["baz"].inner, fields.Int)

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

    def test_is_list_sequence(self):
        assert BaseSchema.is_list_sequence(list)
        assert not BaseSchema.is_list_sequence(tuple)
        assert not BaseSchema.is_list_sequence(bytes)
        assert not BaseSchema.is_list_sequence(str)
        assert not BaseSchema.is_list_sequence(int)
