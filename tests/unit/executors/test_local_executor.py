import pytest

from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact
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
        output = executor.execute(tool.test, {"test": "test"})

        assert isinstance(output, TextArtifact)
        assert output.to_text() == "ack test"

    def test_execute_error_artifact(self, executor, tool):
        output = executor.execute(tool.test_error, {"test": "test"})

        assert isinstance(output, ErrorArtifact)
        assert output.to_text() == "error test"

    def test_execute_str_output(self, executor, tool):
        output = executor.execute(tool.test_str_output, {"test": "test"})

        assert isinstance(output, InfoArtifact)
        assert output.to_text() == "ack test"
