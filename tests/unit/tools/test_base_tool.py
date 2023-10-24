import inspect
import os
import pytest
import yaml
from schema import SchemaMissingKeyError
from griptape.tasks import ActionSubtask
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestBaseTool:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello", test_int=5, test_dict={"foo": "bar"}
        )

    def test_manifest_path(self, tool):
        assert tool.manifest_path == os.path.join(
            tool.abs_dir_path, tool.MANIFEST_FILE
        )

    def test_requirements_path(self, tool):
        assert tool.requirements_path == os.path.join(
            tool.abs_dir_path, tool.REQUIREMENTS_FILE
        )

    def test_manifest(self, tool):
        with open(tool.manifest_path, "r") as yaml_file:
            assert tool.manifest == yaml.safe_load(yaml_file)

    def test_abs_file_path(self, tool):
        assert tool.abs_file_path == os.path.abspath(
            inspect.getfile(tool.__class__)
        )

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

    def test_memory(self):
        tool = MockTool(
            output_memory={
                "test": [
                    defaults.text_tool_memory("Memory1"),
                    defaults.text_tool_memory("Memory2"),
                ]
            }
        )

        assert len(tool.output_memory["test"]) == 2

    def test_memory_validation(self):
        with pytest.raises(ValueError):
            MockTool(
                output_memory={
                    "test": [
                        defaults.text_tool_memory("Memory1"),
                        defaults.text_tool_memory("Memory1"),
                    ]
                }
            )

        with pytest.raises(ValueError):
            MockTool(
                output_memory={
                    "output_memory": [defaults.text_tool_memory("Memory1")]
                }
            )

        assert MockTool(
            output_memory={
                "test": [defaults.text_tool_memory("Memory1")],
                "test_str_output": [defaults.text_tool_memory("Memory1")],
            }
        )

    def test_find_input_memory(self):
        assert MockTool().find_input_memory("foo") is None
        assert (
            MockTool(
                input_memory=[defaults.text_tool_memory("foo")]
            ).find_input_memory("foo")
            is not None
        )

    def test_execute(self, tool):
        assert (
            tool.execute(tool.test_list_output, ActionSubtask("foo")).to_text()
            == "foo\n\nbar"
        )
