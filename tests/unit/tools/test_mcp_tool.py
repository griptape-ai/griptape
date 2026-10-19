import asyncio
import json
from contextlib import asynccontextmanager
from datetime import timedelta
from functools import partial
from typing import TYPE_CHECKING

import anyio
import httpx2
import pytest
from mcp import ClientSession
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.shared.memory import create_client_server_memory_streams

from griptape.artifacts import AudioArtifact, ErrorArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.tools.mcp.sessions import create_session
from griptape.tools.mcp.tool import MCPTool

if TYPE_CHECKING:
    from griptape.tools.mcp.sessions import StdioConnection, StreamableHttpConnection


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

    @pytest.mark.parametrize(
        ("content", "artifact_type", "expected_format"),
        [
            ({"type": "image", "data": "aGk=", "mimeType": "image/gif"}, ImageArtifact, "gif"),
            ({"type": "image", "data": "aGk=", "mimeType": "image/apng"}, ImageArtifact, "apng"),
            ({"type": "image", "data": "aGk=", "mimeType": "image/png"}, ImageArtifact, "png"),
            ({"type": "audio", "data": "aGk=", "mimeType": "audio/aac"}, AudioArtifact, "aac"),
            ({"type": "audio", "data": "aGk=", "mimeType": "audio/wav"}, AudioArtifact, "wav"),
        ],
    )
    def test_media_subtype_removes_only_the_media_prefix(self, tool, content, artifact_type, expected_format):
        """Keep subtype characters that overlap a MIME prefix."""
        artifact = tool._convert_call_tool_result_to_artifact(call_tool_result(content=[content]))

        assert isinstance(artifact.value[0], artifact_type)
        assert artifact.value[0].format == expected_format


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


async def call_over_streamable_http(*, terminate_on_close: bool = True) -> dict:
    """Drives `create_session` against an in-process streamable HTTP server.

    The server is mounted as the ASGI app of the httpx2 client the connection
    builds, so the transport wiring runs without binding a port.
    """
    server = Server("test-server", on_list_tools=list_tools, on_call_tool=call_tool)
    manager = StreamableHTTPSessionManager(app=server)
    observed: dict = {"methods": []}

    async def asgi_app(scope, receive, send) -> None:
        await manager.handle_request(scope, receive, send)

    async def record_request(request: httpx2.Request) -> None:
        observed["methods"].append(request.method)

    def httpx_client_factory(headers=None, timeout=None, auth=None) -> httpx2.AsyncClient:
        observed["headers"] = headers
        observed["timeout"] = timeout
        return httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=asgi_app),
            headers=headers,
            timeout=timeout,
            auth=auth,
            event_hooks={"request": [record_request]},
        )

    connection: StreamableHttpConnection = {  # pyright: ignore[reportAssignmentType]
        "transport": "streamable_http",
        "url": "http://testserver/mcp",
        "headers": {"X-Test": "1"},
        "timeout": 5,
        "sse_read_timeout": timedelta(seconds=10),
        "terminate_on_close": terminate_on_close,
        "httpx_client_factory": httpx_client_factory,
    }

    async with manager.run(), create_session(connection) as session:
        await session.initialize()
        observed["tools"] = [tool.name for tool in (await session.list_tools()).tools]
        content = (await session.call_tool("add-numbers", {"a": 17, "b": 25})).content[0]
        assert isinstance(content, mcp_types.TextContent)
        observed["result"] = content.text

    return observed


class TestStreamableHttpSession:
    def test_session_calls_tools_over_streamable_http(self):
        observed = asyncio.run(call_over_streamable_http())

        assert observed["tools"] == ["add-numbers", "explode"]
        assert observed["result"] == "42"

    def test_connection_configures_the_http_client(self):
        observed = asyncio.run(call_over_streamable_http())

        assert observed["headers"] == {"X-Test": "1"}
        # `sse_read_timeout` becomes the read timeout, whether given as seconds or a timedelta.
        assert observed["timeout"] == httpx2.Timeout(5.0, read=10.0)

    def test_terminate_on_close_deletes_the_session(self):
        assert "DELETE" in asyncio.run(call_over_streamable_http())["methods"]
        assert "DELETE" not in asyncio.run(call_over_streamable_http(terminate_on_close=False))["methods"]
