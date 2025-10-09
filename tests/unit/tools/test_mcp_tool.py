from schema import Or

from griptape.tools.mcp.tool import get_json_schema_value


class TestMCPTool:
    def test_get_json_schema_value_anyof_with_array(self):
        """Test that anyOf with array types properly preserves items type."""
        # This simulates the schema from Maya MCP's mesh_operations tool
        original_schema = {
            "properties": {
                "select_components": {
                    "anyOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "string"},
                    ],
                    "description": "Component selection",
                }
            },
            "required": [],
        }

        result = get_json_schema_value(original_schema)

        # Verify the schema key exists (it's an Optional since not in required)
        assert len(result) == 1
        schema_key = list(result.keys())[0]
        # schema_key is an Optional, and Optional.schema is a Literal
        assert schema_key.schema.schema == "select_components"
        assert schema_key.schema._description == "Component selection"

        # Verify the schema value is an Or with proper types
        schema_value = result[schema_key]
        assert isinstance(schema_value, Or)
        # The Or should contain list[str] and str
        assert list[str] in schema_value._args
        assert str in schema_value._args

    def test_get_json_schema_value_anyof_with_multiple_array_types(self):
        """Test that anyOf with different array item types works correctly."""
        original_schema = {
            "properties": {
                "values": {
                    "anyOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "array", "items": {"type": "integer"}},
                        {"type": "string"},
                    ]
                }
            }
        }

        result = get_json_schema_value(original_schema)

        schema_key = list(result.keys())[0]
        schema_value = result[schema_key]
        assert isinstance(schema_value, Or)
        assert list[str] in schema_value._args
        assert list[int] in schema_value._args
        assert str in schema_value._args

    def test_get_json_schema_value_anyof_with_object(self):
        """Test that anyOf with bare object types works correctly."""
        original_schema = {
            "properties": {
                "param": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "object"},  # Bare object, no properties
                    ]
                }
            }
        }

        result = get_json_schema_value(original_schema)

        schema_key = list(result.keys())[0]
        schema_value = result[schema_key]
        assert isinstance(schema_value, Or)
        assert str in schema_value._args
        assert dict in schema_value._args

    def test_get_json_schema_value_anyof_bare_array(self):
        """Test that anyOf with bare arrays defaults to string items."""
        original_schema = {
            "properties": {
                "values": {
                    "anyOf": [
                        {"type": "array"},  # Bare array, no items specified
                        {"type": "string"},
                    ]
                }
            }
        }

        result = get_json_schema_value(original_schema)

        schema_key = list(result.keys())[0]
        schema_value = result[schema_key]
        # Should default to list[str] for bare arrays
        assert isinstance(schema_value, Or)
        assert list[str] in schema_value._args
        assert str in schema_value._args

    def test_get_json_schema_value_maya_attribute_value(self):
        """Test the Maya MCP set_object_attribute.attribute_value case."""
        # This is the actual schema from Maya MCP that was causing the error
        original_schema = {
            "properties": {
                "attribute_value": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "integer"},
                        {"type": "number"},
                        {"type": "boolean"},
                        {"type": "array"},  # Bare array - will default to list[str]
                        {"type": "object"},  # Bare object - will be dict
                    ]
                }
            },
            "required": ["attribute_value"],
        }

        result = get_json_schema_value(original_schema)

        # Should have one key (not optional since it's required)
        assert len(result) == 1
        schema_key = list(result.keys())[0]
        # Should be Literal, not Optional since it's required
        assert schema_key.schema == "attribute_value"

        # Should process all types with bare array/object getting defaults
        schema_value = result[schema_key]
        assert isinstance(schema_value, Or)
        assert str in schema_value._args
        assert int in schema_value._args
        assert float in schema_value._args
        assert bool in schema_value._args
        assert list[str] in schema_value._args  # Bare array defaults to list[str]
        assert dict in schema_value._args
