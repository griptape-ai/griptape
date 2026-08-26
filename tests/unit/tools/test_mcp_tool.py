import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

mcp_types = pytest.importorskip("mcp.types", reason="mcp package not installed")

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact  # noqa: E402
from griptape.tools.mcp.tool import MCPTool  # noqa: E402


@pytest.fixture()
def tool():
    mock_tool = MagicMock()
    mock_tool.name = "test_tool"
    mock_tool.description = "A test tool"
    mock_tool.title = None
    mock_tool.inputSchema = {"type": "object", "properties": {}}

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[mock_tool]))

    with patch.object(MCPTool, "_get_session") as mock_get_session:
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_get_session.return_value = mock_ctx
        instance = MCPTool.__new__(MCPTool)
        object.__setattr__(instance, "connection", MagicMock())

    return instance


class TestMCPTool:
    def test_text_content_returned(self, tool):
        result = mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text="hello world")],
        )
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)
        assert artifact.value[0].value == "hello world"

    def test_structured_content_only_returns_json_text(self, tool):
        """structuredContent-only result must not silently return empty ListArtifact."""
        payload = {"items": [1, 2, 3], "status": "ok"}
        result = mcp_types.CallToolResult(content=[], structured_content=payload)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)
        assert json.loads(artifact.value[0].value) == payload

    def test_content_takes_priority_over_structured_content(self, tool):
        """When both content and structuredContent are present, content wins."""
        result = mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text="from content")],
            structured_content={"ignored": True},
        )
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert artifact.value[0].value == "from content"

    def test_error_result_with_content(self, tool):
        result = mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text="something went wrong")],
            is_error=True,
        )
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert "something went wrong" in artifact.value

    def test_error_result_with_empty_content_does_not_raise(self, tool):
        """Empty content on an error result must not raise IndexError."""
        result = mcp_types.CallToolResult(content=[], is_error=True)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.value == "An unknown error occurred."

    def test_empty_result_returns_empty_list_artifact(self, tool):
        result = mcp_types.CallToolResult(content=[])
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert artifact.value == []
