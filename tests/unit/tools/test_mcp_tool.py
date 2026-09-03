import json
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING

import anyio
import pytest
from mcp import ClientSession
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.shared.memory import create_client_server_memory_streams

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools.mcp.tool import MCPTool

if TYPE_CHECKING:
    from griptape.tools.mcp.sessions import StdioConnection


def call_tool_result(**payload) -> mcp_types.CallToolResult:
    """Build a CallToolResult from a wire payload.

    Deserializing the camelCase JSON an MCP server actually sends, rather than
    passing Python kwargs, keeps the test honest about the wire format, which is
    unchanged even though the model attributes are snake_case.
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


SERVER_TOOLS = [
    mcp_types.Tool(
        name="add-numbers",
        description="Adds two numbers.",
        input_schema={
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    ),
    mcp_types.Tool(
        name="explode",
        description="Always fails.",
        input_schema={"type": "object", "properties": {}},
    ),
]


async def list_tools(_ctx, _params) -> mcp_types.ListToolsResult:
    return mcp_types.ListToolsResult(tools=SERVER_TOOLS)


async def call_tool(_ctx, params: mcp_types.CallToolRequestParams) -> mcp_types.CallToolResult:
    if params.name == "explode":
        return mcp_types.CallToolResult(content=[mcp_types.TextContent(text="boom")], is_error=True)
    arguments = params.arguments or {}
    total = arguments["a"] + arguments["b"]
    return mcp_types.CallToolResult(content=[mcp_types.TextContent(text=str(total))])


@asynccontextmanager
async def memory_session():
    """Connects a ClientSession to an in-process MCP server over memory streams."""
    server = Server("test-server", on_list_tools=list_tools, on_call_tool=call_tool)

    async with (
        create_client_server_memory_streams() as (
            (client_read, client_write),
            (server_read, server_write),
        ),
        anyio.create_task_group() as task_group,
    ):
        task_group.start_soon(partial(server.run, server_read, server_write, server.create_initialization_options()))
        async with ClientSession(client_read, client_write) as session:
            yield session
        task_group.cancel_scope.cancel()


class InMemoryMCPTool(MCPTool):
    def _get_session(self):
        return memory_session()


class TestMCPToolSession:
    @pytest.fixture()
    def tool(self):
        # `connection` is unused because `_get_session` is overridden.
        connection: StdioConnection = {  # pyright: ignore[reportAssignmentType]
            "transport": "stdio",
            "command": "unused",
            "args": [],
        }
        return InMemoryMCPTool(connection=connection)

    def test_activities_mirror_server_tools(self, tool):
        activities = {activity.config["name"]: activity.config["description"] for activity in tool.activities()}

        assert activities == {"add_numbers": "Adds two numbers.", "explode": "Always fails."}

    def test_activity_schema_from_tool_input_schema(self, tool):
        schema = tool.to_activity_json_schema(tool.add_numbers, "Schema")

        properties = schema["properties"]
        assert properties["a"]["type"] == "integer"
        assert properties["b"]["type"] == "integer"

    def test_call_tool_returns_artifact(self, tool):
        artifact = tool.add_numbers({"values": {"a": 17, "b": 25}})

        assert isinstance(artifact, ListArtifact)
        assert artifact.value[0].value == "42"

    def test_error_result_returns_error_artifact(self, tool):
        artifact = tool.explode({"values": {}})

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.value == "boom"
