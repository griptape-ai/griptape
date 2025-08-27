from __future__ import annotations

import asyncio
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable

from attrs import define, field
from schema import Literal, Optional, Or, Schema

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

from .sessions import Connection, create_session

if TYPE_CHECKING:
    from contextlib import _AsyncGeneratorContextManager

    from mcp import ClientSession, types  # pyright: ignore[reportAttributeAccessIssue]


ANY_TYPE = Or(str, int, float, bool, list, dict)


def json_to_python_type(json_type: str) -> type:
    conversion_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    return conversion_map[json_type]


def get_json_schema_value(original_schema: dict) -> dict:
    json_schema_value = {}
    if "properties" not in original_schema:
        return json_schema_value

    for property_key, property_value in original_schema["properties"].items():
        schema_key = Literal(
            property_key,
            description=property_value.get("description", None),
        )
        schema_value = ANY_TYPE
        if property_key not in original_schema.get("required", []):
            schema_key = Optional(schema_key)
        if "type" in property_value:
            if property_value["type"] == "array":
                item_type = property_value["items"].get("type", "string")
                schema_value = list[json_to_python_type(item_type)]
            elif property_value["type"] == "object":
                schema_value = get_json_schema_value(property_value)
            else:
                schema_value = json_to_python_type(property_value["type"])
        elif "anyOf" in property_value:
            any_of_types = set()
            for item in property_value["anyOf"]:
                if "type" in item:
                    any_of_types.add(json_to_python_type(item["type"]))
                    schema_value = Or(*any_of_types)
        json_schema_value[schema_key] = schema_value
    return json_schema_value


@define
class MCPTool(BaseTool):
    """MCP activities through a tool.

    Attributes:
        connection: The MCP server connection info.
    """

    connection: Connection = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, create a task
            loop.create_task(self._init_activities())
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            asyncio.run(self._init_activities())

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

        @activity(
            config={
                "name": tool.name,
                "description": tool.description or tool.title or tool.name,
                "schema": Schema(get_json_schema_value(tool.inputSchema)),
            }
        )
        def activity_handler(self: MCPTool, values: dict) -> Any:
            try:
                asyncio.get_running_loop()
                # We're in an async context, need to handle this differently
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._run_activity(tool.name, values))
                    return future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(self._run_activity(tool.name, values))

        return activity_handler

    async def _run_activity(self, activity_name: str, params: dict) -> BaseArtifact:
        """Runs an activity on the MCP Server with the provided parameters."""
        try:
            async with self._get_session() as session:
                await session.initialize()
                tool_result = await session.call_tool(activity_name, params)
            return self._convert_call_tool_result_to_artifact(tool_result)
        except Exception as e:
            return ErrorArtifact(value=str(e), exception=e)

    def _convert_call_tool_result_to_artifact(
        self, call_tool_result: types.CallToolResult
    ) -> ListArtifact | ErrorArtifact:
        from mcp import types  # pyright: ignore[reportAttributeAccessIssue]

        if call_tool_result.isError:
            return ErrorArtifact(call_tool_result.content[0].text or "An unknown error occurred.")

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
