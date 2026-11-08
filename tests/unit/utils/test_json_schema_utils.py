import re
from contextlib import nullcontext

import pytest

from griptape.utils.json_schema_utils import build_strict_schema, resolve_refs


class TestJsonSchemaUtils:
    @pytest.mark.parametrize(
        ("output_json_schema", "expected_json_schema", "expected_exception"),
        [
            (
                {
                    "$defs": {
                        "NestedOutputSchema": {"properties": {}, "title": "NestedOutputSchema", "type": "object"}
                    },
                    "properties": {"foo": {"$ref": "#/$defs/NestedOutputSchema"}},
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                {
                    "$id": "OutputSchema",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "properties": {
                        "foo": {
                            "additionalProperties": False,
                            "properties": {},
                            "title": "NestedOutputSchema",
                            "type": "object",
                        },
                    },
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                nullcontext(),
            ),
            (
                {
                    "properties": {
                        "foo": {
                            "additionalProperties": False,
                            "properties": {},
                            "title": "NestedOutputSchema",
                            "type": "object",
                        }
                    },
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                {
                    "$id": "OutputSchema",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "properties": {
                        "foo": {
                            "additionalProperties": False,
                            "properties": {},
                            "title": "NestedOutputSchema",
                            "type": "object",
                        },
                    },
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                nullcontext(),
            ),
        ],
    )
    def test_build_strict_schema(self, output_json_schema, expected_json_schema, expected_exception):
        with expected_exception:
            strict_json_schema = build_strict_schema(output_json_schema, "OutputSchema")
            assert strict_json_schema == expected_json_schema

    @pytest.mark.parametrize(
        ("output_json_schema", "expected_json_schema", "expected_exception"),
        [
            (
                {
                    "$defs": {
                        "NestedOutputSchema": {"properties": {}, "title": "NestedOutputSchema", "type": "object"}
                    },
                    "properties": {"foo": {"$ref": "#/$defs/NestedOutputSchema"}},
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                {
                    "$defs": {
                        "NestedOutputSchema": {"properties": {}, "title": "NestedOutputSchema", "type": "object"}
                    },
                    "properties": {
                        "foo": {
                            "properties": {},
                            "title": "NestedOutputSchema",
                            "type": "object",
                        },
                    },
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                nullcontext(),
            ),
            (
                {
                    "$defs": {},
                    "properties": {"foo": {"$ref": "#/$defs/NestedOutputSchema"}},
                    "required": ["foo"],
                    "title": "OutputSchema",
                    "type": "object",
                },
                None,
                pytest.raises(KeyError, match=re.escape("Definition 'NestedOutputSchema' not found in $defs.")),
            ),
        ],
    )
    def test_resolve_refs(self, output_json_schema, expected_json_schema, expected_exception):
        with expected_exception:
            strict_json_schema = resolve_refs(output_json_schema)
            assert strict_json_schema == expected_json_schema


class TestRecursiveSchema:
    def test_self_referential_definition_is_reported(self):
        schema = {
            "$defs": {
                "Node": {
                    "type": "object",
                    "properties": {"children": {"type": "array", "items": {"$ref": "#/$defs/Node"}}},
                }
            },
            "type": "object",
            "properties": {"root": {"$ref": "#/$defs/Node"}},
        }

        with pytest.raises(ValueError, match="Recursive JSON schema"):
            resolve_refs(schema)

    def test_mutually_recursive_definitions_are_reported(self):
        schema = {
            "$defs": {
                "A": {"type": "object", "properties": {"b": {"$ref": "#/$defs/B"}}},
                "B": {"type": "object", "properties": {"a": {"$ref": "#/$defs/A"}}},
            },
            "type": "object",
            "properties": {"a": {"$ref": "#/$defs/A"}},
        }

        with pytest.raises(ValueError, match="Recursive JSON schema"):
            resolve_refs(schema)

    def test_a_definition_used_twice_is_not_recursive(self):
        schema = {
            "$defs": {"Leaf": {"type": "object", "properties": {"value": {"type": "string"}}}},
            "type": "object",
            "properties": {
                "left": {"$ref": "#/$defs/Leaf"},
                "right": {"$ref": "#/$defs/Leaf"},
            },
        }

        resolved = resolve_refs(schema)

        assert resolved["properties"]["left"] == {"type": "object", "properties": {"value": {"type": "string"}}}
        assert resolved["properties"]["right"] == resolved["properties"]["left"]
