import pytest

from griptape.tools.query.tool import QueryTool
from tests.utils import defaults


class TestQueryTool:
    @pytest.fixture()
    def tool(self):
        return QueryTool(input_memory=[defaults.text_task_memory("TestMemory")])

    def test_query_str(self, tool):
        assert tool.query({"values": {"query": "test", "content": "foo"}}).value[0].value == "mock output"

    def test_query_artifacts(self, tool):
        assert (
            tool.query(
                {
                    "values": {
                        "query": "test",
                        "content": {
                            "memory_name": tool.input_memory[0].name,
                            "artifact_namespace": "test",
                        },
                    }
                }
            )
            .value[0]
            .value
            == "mock output"
        )
