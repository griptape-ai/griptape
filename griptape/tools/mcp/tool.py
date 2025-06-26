from __future__ import annotations

from asyncio import get_event_loop
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from types import MethodType
from typing import Any, Callable
from attrs import define, field
from mcp import ClientSession
import mcp.types as types

from griptape.artifacts import (
    AudioArtifact,
    BaseArtifact,
    BlobArtifact,
    ErrorArtifact,
    ImageArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

from .sessions import create_session, Connection


@define
class MCPTool(BaseTool):
    """MCP activities through a tool.

    Attributes:
        connection: The MCP server connection info.
    """

    connection: Connection = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        get_event_loop().run_until_complete(self._init_activities())

    async def _init_activities(self) -> None:
        async with self._get_session() as session:
            await session.initialize()
            tools_response = await session.list_tools()

        for tool in tools_response.tools:
            activity_handler = self._create_activity_handler(tool)
            setattr(self, tool.name, MethodType(activity_handler, self))

    def _get_session(self) -> _AsyncGeneratorContextManager[ClientSession, None]:
        return create_session(self.connection)

    def _create_activity_handler(self, tool: types.Tool) -> Callable:
        """Creates an activity handler method for the MCP tool."""

        @activity(config={"name": tool.name, "description": tool.description, "schema": tool.inputSchema})
        def activity_handler(self: MCPTool, values: dict) -> Any:
            return self._run_activity(tool.name, values)

        return activity_handler

    async def _run_activity(self, activity_name: str, params: dict) -> BaseArtifact:
        """Runs an activity on the MCP Server with the provided parameters."""
        try:
            async with create_session(self.connection) as session:
                await session.initialize()
                tool_result = await session.call_tool(activity_name, params)
            return self._convert_call_tool_result_to_artifact(tool_result)
        except Exception as e:
            return ErrorArtifact(value=str(e), exception=e)

    def _convert_call_tool_result_to_artifact(
        self, call_tool_result: types.CallToolResult
    ) -> ListArtifact | ErrorArtifact:
        if call_tool_result.isError:
            return ErrorArtifact(call_tool_result.content)

        response_artifacts: list[BaseArtifact] = []
        for content in call_tool_result.content:
            if isinstance(content, types.TextContent):
                response_artifacts.append(TextArtifact(content.text))
            elif isinstance(content, types.ImageContent):
                response_artifacts.append(
                    ImageArtifact(value=content.data, format=content.mimeType.lstrip("image/"), width=0, height=0)
                )
            elif isinstance(content, types.AudioContent):
                response_artifacts.append(AudioArtifact(value=content.data, format=content.mimeType.lstrip("audio/")))
            elif isinstance(content, types.EmbeddedResource):
                if isinstance(content.resource, types.TextResourceContents):
                    response_artifacts.append(TextArtifact(content.resource.text))
                elif isinstance(content.resource, types.BlobResourceContents):
                    response_artifacts.append(BlobArtifact(value=content.resource.blob))

        return ListArtifact(response_artifacts)
