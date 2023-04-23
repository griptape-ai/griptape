import pytest
import langchain.tools
from griptape.core.adapters import LangchainToolAdapter
from griptape.core.executors import LocalExecutor
from tests.mocks.mock_tool.tool import MockTool


class TestLangchainToolAdapter:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello"
        )

    @pytest.fixture
    def executor(self):
        return LocalExecutor()

    def test_generate(self, tool, executor):
        assert isinstance(LangchainToolAdapter(executor=executor).generate_tool(tool.test), langchain.tools.BaseTool)

    def test_run(self, tool, executor):
        assert LangchainToolAdapter(executor=executor).generate_tool(tool.test)._run("test") == "ack test"
