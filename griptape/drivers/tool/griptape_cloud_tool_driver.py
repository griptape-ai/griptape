from __future__ import annotations

import os
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable
from urllib.parse import urljoin

import requests
from attrs import Factory, define, field
from schema import Literal, Optional, Schema

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers.tool.base_tool_driver import BaseToolDriver
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.tools.base_tool import BaseTool


@define
class GriptapeCloudToolDriver(BaseToolDriver):
    """Driver for interacting with tools hosted on the Griptape Cloud.

    Attributes:
        base_url: Base URL of the Griptape Cloud.
        api_key: API key for the Griptape Cloud.
        tool_id: ID of the tool to interact with.
        headers: Headers to use for requests.
    """

    base_url: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")))
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    tool_id: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )

    def initialize_tool(self, tool: BaseTool) -> None:
        schema = self._get_schema()
        tool_name, activity_schemas = self._parse_schema(schema)

        if tool.name == tool.__class__.__name__:
            tool.name = tool_name

        for activity_name, (description, activity_schema) in activity_schemas.items():
            activity_handler = self._create_activity_handler(activity_name, description, activity_schema)

            setattr(tool, activity_name, MethodType(activity_handler, self))

    def _get_schema(self) -> dict:
        url = urljoin(self.base_url, f"/api/tools/{self.tool_id}/openapi")
        response = requests.get(url, headers=self.headers)

        response.raise_for_status()

        return response.json()

    def _parse_schema(self, schema: dict) -> tuple[str, dict[str, tuple[str, Schema]]]:
        """Parses an openapi schema into a dictionary of activity names and their respective descriptions + schemas."""
        activities = {}

        name = schema.get("info", {}).get("title")

        for path, path_info in schema.get("paths", {}).items():
            if not path.startswith("/activities"):
                continue
            for method, method_info in path_info.items():
                if "post" in method.lower():
                    activity_name = method_info["operationId"]
                    description = method_info.get("description", "")

                    activity_schema = self.__extract_schema_from_ref(
                        schema,
                        method_info.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {}),
                    )

                    activities[activity_name] = (description, activity_schema)

        return name, activities

    def __extract_schema_from_ref(self, schema: dict, schema_ref: dict) -> Schema:
        """Extracts a schema from a $ref if present, resolving it into native schema properties."""
        if "$ref" in schema_ref:
            # Resolve the reference and retrieve the schema data
            ref_path = schema_ref["$ref"].split("/")[-1]
            schema_data = schema["components"]["schemas"].get(ref_path, {})
        else:
            # Use the provided schema directly if no $ref is found
            schema_data = schema_ref

        # Convert the schema_data dictionary into a Schema with its properties
        properties = {}
        for prop, prop_info in schema_data.get("properties", {}).items():
            prop_type = prop_info.get("type", "string")
            prop_description = prop_info.get("description", "")
            schema_prop = Literal(prop, description=prop_description)
            is_optional = prop not in schema_data.get("required", [])

            if is_optional:
                schema_prop = Optional(schema_prop)

            properties[schema_prop] = self._map_openapi_type_to_python(prop_type)

        return Schema(properties)

    def _map_openapi_type_to_python(self, openapi_type: str) -> type:
        """Maps OpenAPI types to native Python types."""
        type_mapping = {"string": str, "integer": int, "boolean": bool, "number": float, "array": list, "object": dict}

        return type_mapping.get(openapi_type, str)

    def _create_activity_handler(self, activity_name: str, description: str, activity_schema: Schema) -> Callable:
        """Creates an activity handler method for the tool."""

        @activity(config={"name": activity_name, "description": description, "schema": activity_schema})
        def activity_handler(_: BaseTool, values: dict) -> Any:
            return self._run_activity(activity_name, values)

        return activity_handler

    def _run_activity(self, activity_name: str, params: dict) -> BaseArtifact:
        """Runs an activity on the tool with the provided parameters."""
        url = urljoin(self.base_url, f"/api/tools/{self.tool_id}/activities/{activity_name}")

        response = requests.post(url, json=params, headers=self.headers)

        response.raise_for_status()

        try:
            return BaseArtifact.from_dict(response.json())
        except ValueError:
            return TextArtifact(response.text)
