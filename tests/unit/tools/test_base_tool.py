import inspect
import os
import tempfile
from unittest.mock import Mock

import pytest
from attrs import define
from schema import Or, Schema, SchemaMissingKeyError

from griptape.artifacts.info_artifact import InfoArtifact
from griptape.common import ToolAction
from griptape.tasks import ActionsSubtask, PromptTask
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_tool_kwargs.tool import MockToolKwargs
from tests.utils import defaults


class TestBaseTool:
    TARGET_TOOL_SCHEMA = {
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
                    "path": {"description": "test description", "const": "test_callable_schema"},
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
                    "path": {"description": "test description: foo", "const": "test_exception"},
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
                    "input": {"additionalProperties": False, "properties": {}, "required": [], "type": "object"},
                },
                "required": ["name", "path"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "name": {"const": "MockTool"},
                    "path": {"description": "test description", "const": "test_no_schema"},
                    "input": {"additionalProperties": False, "properties": {}, "required": [], "type": "object"},
                },
                "required": ["name", "path"],
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
        "$id": "MockTool ToolAction Schema",
        "$schema": "http://json-schema.org/draft-07/schema#",
    }

    @pytest.fixture()
    def tool(self):
        return MockTool(test_field="hello", test_int=5, test_dict={"foo": "bar"})

    def test_off_prompt(self, tool):
        assert (
            not PromptTask(task_memory=defaults.text_task_memory("TestMemory"), tools=[MockTool()])
            .tools[0]
            .output_memory
        )

        assert (
            PromptTask(task_memory=defaults.text_task_memory("TestMemory"), tools=[MockTool(off_prompt=True)])
            .tools[0]
            .output_memory
        )

    def test_requirements_path(self, tool):
        assert tool.requirements_path == os.path.join(tool.abs_dir_path, tool.REQUIREMENTS_FILE)

    def test_abs_file_path(self, tool):
        assert tool.abs_file_path == os.path.abspath(inspect.getfile(tool.__class__))

    def test_abs_dir_path(self, tool):
        assert tool.abs_dir_path == os.path.dirname(tool.abs_file_path)

    def test_name(self):
        assert MockTool().name == "MockTool"
        assert MockTool(name="FooBar").name == "FooBar"

    def test_validate(self, tool):
        assert tool.validate()

    def test_invalid_config(self):
        try:
            from tests.mocks.invalid_mock_tool.tool import InvalidMockTool  # noqa: F401

            raise AssertionError
        except SchemaMissingKeyError:
            assert True

    def test_memory(self):
        tool = MockTool(
            output_memory={"test": [defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory2")]}
        )

        assert tool.output_memory is not None
        assert len(tool.output_memory["test"]) == 2

    def test_memory_validation(self):
        with pytest.raises(ValueError):
            MockTool(
                output_memory={"test": [defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory1")]}
            )

        with pytest.raises(ValueError):
            MockTool(output_memory={"output_memory": [defaults.text_task_memory("Memory1")]})

        assert MockTool(
            output_memory={
                "test": [defaults.text_task_memory("Memory1")],
                "test_str_output": [defaults.text_task_memory("Memory1")],
            }
        )

    def test_find_input_memory(self):
        assert MockTool().find_input_memory("foo") is None
        assert MockTool(input_memory=[defaults.text_task_memory("foo")]).find_input_memory("foo") is not None

    def test_run(self, tool):
        action = ToolAction(input={}, name="", tag="")
        assert tool.run(tool.test_list_output, ActionsSubtask("foo"), action).to_text() == "foo\n\nbar"

    def test_schema(self, tool):
        tool = MockTool()

        assert tool.schema() == self.TARGET_TOOL_SCHEMA

    def test_activity_schemas(self, tool):
        tool = MockTool()

        full_schema = Schema(Or(*tool.activity_schemas()), description=f"{tool.name} action schema.")

        tool_schema = full_schema.json_schema(f"{tool.name} ToolAction Schema")

        assert tool_schema == self.TARGET_TOOL_SCHEMA

    def test_to_native_tool_name(self, tool, mocker):
        tool = MockTool()

        assert tool.to_native_tool_name(tool.test) == "MockTool_test"

        # Bad name
        tool.name = "mock_tool"
        with pytest.raises(ValueError, match="Tool name"):
            tool.to_native_tool_name(tool.foo)

        # Bad activity name
        mocker.patch.object(tool, "activity_name", return_value="foo^bar")
        tool.name = "MockTool"
        with pytest.raises(ValueError, match="Activity name"):
            tool.to_native_tool_name(tool.test)

    def test_to_dict(self, tool):
        tool = MockTool()

        expected_tool_dict = {
            "type": tool.type,
            "name": tool.name,
            "input_memory": tool.input_memory,
            "output_memory": tool.output_memory,
            "install_dependencies_on_init": tool.install_dependencies_on_init,
            "dependencies_install_directory": tool.dependencies_install_directory,
            "verbose": tool.verbose,
            "off_prompt": tool.off_prompt,
        }

        assert expected_tool_dict == tool.to_dict()

    def test_from_dict(self, tool):
        tool = MockTool()
        action = ToolAction(input={}, name="", tag="")

        serialized_tool = tool.to_dict()
        assert isinstance(serialized_tool, dict)

        deserialized_tool = MockTool.from_dict(serialized_tool)
        assert isinstance(deserialized_tool, BaseTool)

        assert deserialized_tool.run(tool.test_list_output, ActionsSubtask("foo"), action).to_text() == "foo\n\nbar"

    def test_method_kwargs_var_injection(self, tool):
        tool = MockToolKwargs()

        params = {"values": {"test_kwarg": "foo", "test_kwarg_kwargs": "bar"}}
        assert tool.test_with_kwargs(params) == "ack foo"

    def test_has_requirements(self, tool):
        assert tool.has_requirements

        class InlineTool(BaseTool):
            pass

        assert InlineTool().has_requirements is False

    def test_are_requirements_met(self, tool):
        assert tool.are_requirements_met(tool.requirements_path)

        class InlineTool(BaseTool):
            pass

        # Temp file does not work on Github Actions Windows runner.
        if os.name != "nt":
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b"nonexistent-package==1.0.0\nanother-package==2.0.0")
                temp.seek(0)

                assert InlineTool().are_requirements_met(temp.name) is False

            with tempfile.NamedTemporaryFile() as temp:
                temp.write(b"pip")
                temp.seek(0)

                assert InlineTool().are_requirements_met(temp.name) is True

    def test_runnable_mixin(self, tool):
        mock_on_before_run = Mock()
        mock_after_run = Mock()
        tool = MockTool(on_before_run=mock_on_before_run, on_after_run=mock_after_run)

        tool.run(tool.test_list_output, ActionsSubtask("foo"), ToolAction(input={}, name="", tag="")).to_text()

        mock_on_before_run.assert_called_once_with(tool)
        mock_after_run.assert_called_once_with(tool)

    def test_frozen_values(self):
        values = {"query": "foo"}

        @define
        class FrozenTool(BaseTool):
            @activity({"description": "Test description"})
            def mutate_values(self, values: dict) -> None:
                values.pop("query")

        tool = FrozenTool()

        tool.run(tool.mutate_values, ActionsSubtask("foo"), ToolAction(input={"values": values}, name="", tag=""))
        assert "query" in values

    def test_artifact_conversion(self, tool):
        tool = MockTool()

        result = tool.run(
            tool.test_no_schema, ActionsSubtask("foo"), ToolAction(input={"values": {"test": "foo"}}, name="", tag="")
        )
        assert isinstance(result, InfoArtifact)
        assert result.value == "no schema"

    def test_no_result(self, tool):
        @define
        class NoResultTool(BaseTool):
            @activity({"description": "Test description"})
            def no_result(self, values: dict) -> None: ...

        tool = NoResultTool()

        result = tool.run(tool.no_result, ActionsSubtask("foo"), ToolAction(input={"values": {}}, name="", tag=""))
        assert isinstance(result, InfoArtifact)
        assert result.value == "Tool returned an empty value"
