import json

import pytest
from mcp import types as mcp_types

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools.mcp.tool import MCPTool


def call_tool_result(**payload) -> mcp_types.CallToolResult:
    """Build a CallToolResult from a wire payload.

    Deserializing the JSON an MCP server actually sends, rather than passing
    Python kwargs, keeps the test honest: `CallToolResult` allows extra fields,
    so a misspelled kwarg would be silently accepted as a new attribute.
    """
    return mcp_types.CallToolResult.model_validate({"content": [], **payload})


@pytest.fixture()
def tool():
    # __new__ skips __attrs_post_init__, which would otherwise open a server session.
    return MCPTool.__new__(MCPTool)


class TestMCPTool:
    def test_text_content_returned(self, tool):
        result = call_tool_result(content=[{"type": "text", "text": "hello world"}])
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)
        assert artifact.value[0].value == "hello world"

    def test_structured_content_only_returns_json_text(self, tool):
        """structuredContent-only result must not silently return an empty ListArtifact."""
        payload = {"items": [1, 2, 3], "status": "ok"}
        result = call_tool_result(structuredContent=payload)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)
        assert json.loads(artifact.value[0].value) == payload

    def test_content_takes_priority_over_structured_content(self, tool):
        """When both content and structuredContent are present, content wins."""
        result = call_tool_result(
            content=[{"type": "text", "text": "from content"}],
            structuredContent={"ignored": True},
        )
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert artifact.value[0].value == "from content"

    def test_error_result_with_content(self, tool):
        result = call_tool_result(content=[{"type": "text", "text": "something went wrong"}], isError=True)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert "something went wrong" in artifact.value

    def test_error_result_with_empty_content_does_not_raise(self, tool):
        """Empty content on an error result must not raise IndexError."""
        result = call_tool_result(isError=True)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.value == "An unknown error occurred."

    def test_error_result_with_non_text_content_does_not_raise(self, tool):
        """A non-text first block on an error result must not raise AttributeError."""
        result = call_tool_result(
            content=[{"type": "image", "data": "aGk=", "mimeType": "image/png"}],
            isError=True,
        )
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.value == "An unknown error occurred."

    def test_error_result_falls_back_to_structured_content(self, tool):
        payload = {"code": 42, "msg": "structured error"}
        result = call_tool_result(isError=True, structuredContent=payload)
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ErrorArtifact)
        assert json.loads(artifact.value) == payload

    def test_empty_result_returns_empty_list_artifact(self, tool):
        result = call_tool_result()
        artifact = tool._convert_call_tool_result_to_artifact(result)

        assert isinstance(artifact, ListArtifact)
        assert artifact.value == []
