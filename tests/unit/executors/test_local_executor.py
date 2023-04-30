import pytest

from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.executors import LocalExecutor
from tests.mocks.mock_tool.tool import MockTool


class TestLocalExecutor:
    @pytest.fixture
    def executor(self):
        return LocalExecutor()

    @pytest.fixture
    def tool(self):
        return MockTool()

    def test_execute_text_artifact(self, executor, tool):
        output = executor.execute(tool.test, TextArtifact("test"))

        assert isinstance(output, TextArtifact)
        assert output.value == "ack test"

    def test_execute_error_artifact(self, executor, tool):
        output = executor.execute(tool.test_error, TextArtifact("test"))

        assert isinstance(output, ErrorArtifact)
        assert output.value == "error test"

    def test_execute_str_output(self, executor, tool):
        output = executor.execute(tool.test_str_output, TextArtifact("test"))

        assert isinstance(output, TextArtifact)
        assert output.value == "ack test"
