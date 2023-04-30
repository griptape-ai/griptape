import pytest

from griptape.artifacts import TextOutput, ErrorOutput
from griptape.executors import LocalExecutor
from tests.mocks.mock_tool.tool import MockTool


class TestLocalExecutor:
    @pytest.fixture
    def executor(self):
        return LocalExecutor()

    @pytest.fixture
    def tool(self):
        return MockTool()

    def test_execute_text_output(self, executor, tool):
        output = executor.execute(tool.test, TextOutput("test"))

        assert isinstance(output, TextOutput)
        assert output.value == "ack test"

    def test_execute_error_output(self, executor, tool):
        output = executor.execute(tool.test_error, TextOutput("test"))

        assert isinstance(output, ErrorOutput)
        assert output.value == "error test"

    def test_execute_str_output(self, executor, tool):
        output = executor.execute(tool.test_str_output, TextOutput("test"))

        assert isinstance(output, TextOutput)
        assert output.value == "ack test"
