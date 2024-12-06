from __future__ import annotations

from types import MethodType
from typing import Any, Callable, Optional
from urllib.parse import urljoin

import requests
from attrs import define, field
from schema import Literal, Schema
from schema import Optional as SchemaOptional

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tools.base_griptape_cloud_tool import BaseGriptapeCloudTool
from griptape.utils.decorators import activity


@define()
class GriptapeCloudToolTool(BaseGriptapeCloudTool):
    """Runs a Griptape Cloud hosted Tool.

    Attributes:
        tool_id: The ID of the tool to run.
    """

    tool_id: str = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        self._init_activities()

    def _init_activities(self) -> None:
        schema = self._get_schema()
        tool_name, activity_schemas = self._parse_schema(schema)

        if self.name == self.__class__.__name__:
            self.name = tool_name

        for activity_name, (description, activity_schema) in activity_schemas.items():
            activity_handler = self._create_activity_handler(activity_name, description, activity_schema)

            setattr(self, activity_name, MethodType(activity_handler, self))

    def _get_schema(self) -> dict:
        response = requests.get(urljoin(self.base_url, f"/api/tools/{self.tool_id}/openapi"), headers=self.headers)

        response.raise_for_status()
        schema = response.json()

        if not isinstance(schema, dict):
            raise RuntimeError(f"Invalid schema for tool {self.tool_id}: {schema}")

        if "error" in schema and "tool_run_id" in schema:
            raise RuntimeError(f"Failed to retrieve schema for tool {self.tool_id}: {schema['error']}")

        return schema

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
                schema_prop = SchemaOptional(schema_prop)

            properties[schema_prop] = self._map_openapi_type_to_python(prop_type, prop_info)

        return Schema(properties)

    def _map_openapi_type_to_python(self, openapi_type: str, schema_info: Optional[dict] = None) -> type | list[type]:
        """Maps OpenAPI types to native Python types."""
        type_mapping = {"string": str, "integer": int, "boolean": bool, "number": float, "object": dict}

        if openapi_type == "array" and schema_info is not None and "items" in schema_info:
            items_type = schema_info["items"].get("type", "string")
            return [self._map_openapi_type_to_python(items_type)]  # pyright: ignore[reportReturnType]
        else:
            return type_mapping.get(openapi_type, str)

    def _create_activity_handler(self, activity_name: str, description: str, activity_schema: Schema) -> Callable:
        """Creates an activity handler method for the tool."""

        @activity(config={"name": activity_name, "description": description, "schema": activity_schema})
        def activity_handler(self: GriptapeCloudToolTool, values: dict) -> Any:
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
