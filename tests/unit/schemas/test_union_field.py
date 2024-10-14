import marshmallow
import pytest
from marshmallow import fields

from griptape.schemas.union_field import UnionField


class InvalidType:
    pass


@pytest.fixture()
def sample_schema():
    class SampleSchema(marshmallow.Schema):
        name = UnionField(fields=[fields.Integer(), fields.String()])

    return SampleSchema()


class TestUnionField:
    def test_union_field_valid_string(self, sample_schema):
        input_data = {"name": "Alice"}
        result = sample_schema.load(input_data)
        assert result["name"] == "Alice"

    def test_union_field_valid_integer(self, sample_schema):
        input_data = {"name": 42}
        result = sample_schema.load(input_data)
        assert result["name"] == 42

    def test_union_field_invalid_value(self, sample_schema):
        input_data = {"name": InvalidType}
        with pytest.raises(marshmallow.exceptions.ValidationError) as exc_info:
            sample_schema.load(input_data)
        assert "name" in exc_info.value.messages
        assert len(exc_info.value.messages["name"]) > 0

    def test_union_field_serialize_string(self, sample_schema):
        input_data = {"name": "Alice"}
        result = sample_schema.dump(input_data)
        assert result["name"] == "Alice"

    def test_union_field_serialize_integer(self, sample_schema):
        input_data = {"name": 42}
        result = sample_schema.dump(input_data)
        assert result["name"] == 42

    def test_union_field_reverse_serialization(self, sample_schema):
        class ReverseSchema(marshmallow.Schema):
            value = UnionField(fields=[fields.Integer(), fields.String()], reverse_serialize_candidates=True)

        schema = ReverseSchema()
        input_data = {"value": "Test"}
        result = schema.dump(input_data)
        assert result["value"] == "Test"
