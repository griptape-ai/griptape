import pytest
import schema

from griptape.tools import StructuredOutputTool


class TestStructuredOutputTool:
    @pytest.fixture()
    def tool(self):
        return StructuredOutputTool(output_schema=schema.Schema({"foo": "bar"}))

    def test_provide_output(self, tool):
        assert tool.provide_output({"values": {"foo": "bar"}}).value == {"foo": "bar"}
