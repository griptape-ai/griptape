from griptape.executors import LocalExecutor
from tests.mocks.mock_tool.tool import MockTool


class TestLocalExecutor:
    def test_execute(self):
        executor = LocalExecutor()
        tool = MockTool()

        assert executor.execute(tool.test, "test") == "ack test"
