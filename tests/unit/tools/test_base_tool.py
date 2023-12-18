import inspect
import os
import pytest
import yaml
from schema import SchemaMissingKeyError
from griptape.tasks import ActionSubtask, ToolkitTask
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestBaseTool:
    @pytest.fixture
    def tool(self):
        return MockTool(test_field="hello", test_int=5, test_dict={"foo": "bar"})

    def test_manifest_path(self, tool):
        assert tool.manifest_path == os.path.join(tool.abs_dir_path, tool.MANIFEST_FILE)

    def test_requirements_path(self, tool):
        assert tool.requirements_path == os.path.join(tool.abs_dir_path, tool.REQUIREMENTS_FILE)

    def test_manifest(self, tool):
        with open(tool.manifest_path) as yaml_file:
            assert tool.manifest == yaml.safe_load(yaml_file)

    def test_abs_file_path(self, tool):
        assert tool.abs_file_path == os.path.abspath(inspect.getfile(tool.__class__))

    def test_abs_dir_path(self, tool):
        assert tool.abs_dir_path == os.path.dirname(tool.abs_file_path)

    def test_name(self):
        assert MockTool().name == "MockTool"
        assert MockTool(name="FooBar").name == "FooBar"

    def test_class_name(self):
        assert MockTool().class_name == "MockTool"
        assert MockTool(name="FooBar").class_name == "MockTool"

    def test_validate(self, tool):
        assert tool.validate()

    def test_invalid_config(self):
        try:
            from tests.mocks.invalid_mock_tool.tool import InvalidMockTool

            assert False
        except SchemaMissingKeyError as e:
            assert True

    def test_execute(self, tool):
        assert tool.execute(tool.test_list_output, ActionSubtask("foo")).to_text() == "foo\n\nbar"

    def test_schema(self, tool):
        tool = MockTool()

        assert tool.schema() == {
            "description": "MockTool action schema.",
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test_error"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_list_output"},
                        "input": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_no_schema"},
                        "input": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test_str_output"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_without_default_memory"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["name", "path", "input"],
                    "additionalProperties": False,
                },
            ],
            "$id": "MockTool Action Schema",
            "$schema": "http://json-schema.org/draft-07/schema#",
        }
