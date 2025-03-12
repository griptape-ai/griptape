from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Union

import pytest
from marshmallow import fields
from pydantic import BaseModel

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.schemas import PolymorphicSchema
from griptape.schemas.base_schema import BaseSchema
from griptape.schemas.bytes_field import Bytes
from griptape.schemas.pydantic_model_field import PydanticModel
from griptape.schemas.union_field import Union as UnionField
from tests.mocks.mock_serializable import MockSerializable


class MockEnum(Enum):
    FOO = ("BAR",)
    BAZ = ("QUX",)
    BAR = ("FOO",)


class UnsupportedType:
    pass


class MockModel(BaseModel):
    foo: str


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

        assert isinstance(BaseSchema._get_field_for_type(BaseModel), PydanticModel)
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
        assert BaseSchema._is_list_sequence(list)
        assert not BaseSchema._is_list_sequence(tuple)
        assert not BaseSchema._is_list_sequence(bytes)
        assert not BaseSchema._is_list_sequence(str)
        assert not BaseSchema._is_list_sequence(int)

    def test_is_union(self):
        assert BaseSchema._is_union(Union[str, int])
        assert BaseSchema._is_union(Union[str, Union[int, str]])
        assert not BaseSchema._is_union(tuple)
        assert not BaseSchema._is_union(bytes)
        assert not BaseSchema._is_union(str)
        assert not BaseSchema._is_union(int)

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

        candidate_fields = [type(f) for f in union_field._candidate_fields]
        assert fields.Str in candidate_fields
        assert fields.List in candidate_fields

    def test_handle_union_outside_list(self):
        field = BaseSchema._get_field_for_type(Union[str, int])
        assert isinstance(field, UnionField)

        candidate_fields = [type(f) for f in field._candidate_fields]
        assert fields.Str in candidate_fields
        assert fields.Integer in candidate_fields

    def test_handle_none(self):
        field = BaseSchema._get_field_for_type(None)
        assert isinstance(field, fields.Constant)
        assert field.allow_none is True
        assert field.constant is None

    def test_is_enum(self):
        result = BaseSchema._is_enum(MockEnum)
        assert result is True

    def test_handle_enum(self):
        field = BaseSchema._get_field_for_type(MockEnum)
        assert isinstance(field, fields.Str)

    def test_handle_optional_enum(self):
        field = BaseSchema._get_field_for_type(Union[MockEnum, None])
        assert isinstance(field, UnionField)
        assert isinstance(field._candidate_fields[0], fields.Str)
        assert field.allow_none is True

    def test_handle_unsupported_type(self):
        assert isinstance(BaseSchema._get_field_for_type(UnsupportedType), fields.Raw)

    def test_handle_union_exception(self):
        with pytest.raises(ValueError, match="Unsupported UnionType field: <class 'NoneType'>"):
            BaseSchema._handle_union(Union[None], optional=False)

    def test_handle_union_optional(self):
        field = BaseSchema._handle_union(Union[str, None], optional=True)
        assert isinstance(field, UnionField)
        assert field.allow_none is True

    def test_serialization_override(self):
        assert "bar" in MockSerializable().to_dict(serializable_overrides={"bar": True})
        assert "bar" not in MockSerializable().to_dict(serializable_overrides={"bar": False})
        assert MockSerializable().to_dict(serializable_overrides={"not_a_key": True})

    def test_types_override(self):
        assert MockSerializable().to_dict(types_overrides={"foo": int})
