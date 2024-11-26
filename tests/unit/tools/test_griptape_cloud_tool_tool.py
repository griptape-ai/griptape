import json

import pytest
import schema

from griptape.artifacts.text_artifact import TextArtifact
from griptape.tools import GriptapeCloudToolTool

MOCK_SCHEMA = {
    "openapi": "3.1.0",
    "info": {"title": "DataProcessor", "version": "0.2.0"},
    "servers": [{"url": "https://cloud.griptape.ai/api/tools/1"}],
    "paths": {
        "/activities/processString": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process String",
                "description": "Processes a string input",
                "operationId": "processString",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/StringInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "String processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processNumber": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process Number",
                "description": "Processes a number input",
                "operationId": "processNumber",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/NumberInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Number processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processBoolean": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process Boolean",
                "description": "Processes a boolean input",
                "operationId": "processBoolean",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BooleanInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Boolean processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processArray": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process Array",
                "description": "Processes an array input",
                "operationId": "processArray",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ArrayInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Array processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processObject": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process Object",
                "description": "Processes an object input",
                "operationId": "processObject",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ObjectInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Object processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processRequired": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process Required",
                "description": "Processes a required input",
                "operationId": "processRequired",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RequiredInput"}}},
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Required processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processNoRef": {
            "post": {
                "tags": ["Activities"],
                "summary": "Process No Ref",
                "description": "Processes a no ref input",
                "operationId": "processNoRef",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "properties": {
                                    "text": {"type": "string", "title": "Text", "description": "The string to process"},
                                },
                                "type": "object",
                                "title": "StringInput",
                            }
                        }
                    },
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Required processed",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BaseArtifact"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
        "/activities/processWrongMethod": {"get": {}},
        "/openapi": {
            "get": {
                "tags": ["OpenAPI"],
                "summary": "OpenAPI Specification",
                "description": "Get the OpenAPI specification for this tool",
                "operationId": "openapi",
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {"type": "object", "title": "Response Openapi"}}},
                    }
                },
                "security": [{"bearerAuth": []}],
            }
        },
    },
    "components": {
        "schemas": {
            "BaseArtifact": {
                "properties": {
                    "value": {"title": "Value", "description": "The return value of the activity"},
                    "type": {"type": "string", "title": "Type", "description": "The type of the return value"},
                },
                "type": "object",
                "required": ["value", "type"],
                "title": "BaseArtifact",
            },
            "ErrorResponse": {
                "properties": {
                    "error": {"type": "string", "title": "Error", "description": "The return value of the activity"}
                },
                "type": "object",
                "required": ["error"],
                "title": "ErrorResponse",
            },
            "StringInput": {
                "properties": {
                    "text": {"type": "string", "title": "Text", "description": "The string to process"},
                },
                "type": "object",
                "title": "StringInput",
            },
            "NumberInput": {
                "properties": {
                    "number": {"type": "number", "title": "Number", "description": "The number to process"},
                },
                "type": "object",
                "title": "NumberInput",
            },
            "BooleanInput": {
                "properties": {
                    "flag": {"type": "boolean", "title": "Flag", "description": "The boolean to process"},
                },
                "type": "object",
                "title": "BooleanInput",
            },
            "ArrayInput": {
                "properties": {
                    "items": {
                        "type": "array",
                        "title": "Items",
                        "description": "An array of numbers",
                        "items": {"type": "number"},
                    }
                },
                "type": "object",
                "title": "ArrayInput",
            },
            "ObjectInput": {
                "properties": {
                    "data": {
                        "type": "object",
                        "title": "Data",
                        "description": "An object containing key-value pairs",
                        "additionalProperties": {"type": "string"},
                    }
                },
                "type": "object",
                "title": "ObjectInput",
            },
            "RequiredInput": {
                "properties": {
                    "required": {
                        "type": "string",
                        "title": "Required",
                        "description": "A required input field",
                    }
                },
                "type": "object",
                "required": ["required"],
                "title": "RequiredInput",
            },
        },
        "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
    },
}


class TestGriptapeCloudToolTool:
    @pytest.fixture()
    def mock_schema(self):
        return MOCK_SCHEMA

    @pytest.fixture(autouse=True)
    def _mock_requests_get(self, mocker, mock_schema):
        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_schema

    @pytest.fixture(autouse=True)
    def _mock_requests_post(self, mocker):
        mock_get = mocker.patch("requests.post")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = TextArtifact("foo").to_dict()

    def test_init(self):
        tool = GriptapeCloudToolTool(tool_id="tool_id")

        # Define expected activity details for each method
        expected_activities = {
            "processString": {
                "name": "processString",
                "description": "Processes a string input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("text", description="The string to process")): str}
                ),
            },
            "processNumber": {
                "name": "processNumber",
                "description": "Processes a number input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("number", description="The number to process")): float}
                ),
            },
            "processBoolean": {
                "name": "processBoolean",
                "description": "Processes a boolean input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("flag", description="The boolean to process")): bool}
                ),
            },
            "processArray": {
                "name": "processArray",
                "description": "Processes an array input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("items", description="An array of numbers")): [float]}
                ),
            },
            "processObject": {
                "name": "processObject",
                "description": "Processes an object input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("data", description="An object containing key-value pairs")): dict}
                ),
            },
            "processRequired": {
                "name": "processRequired",
                "description": "Processes a required input",
                "schema": schema.Schema({schema.Literal("required", description="A required input field"): str}),
            },
            "processNoRef": {
                "name": "processNoRef",
                "description": "Processes a no ref input",
                "schema": schema.Schema(
                    {schema.Optional(schema.Literal("text", description="The string to process")): str}
                ),
            },
        }

        for activity_name, details in expected_activities.items():
            assert hasattr(tool, activity_name), f"Method {activity_name} does not exist in the tool."
            activity = getattr(tool, activity_name)

            assert getattr(activity, "name") == details["name"]
            assert getattr(activity, "config")["name"] == details["name"]
            assert getattr(activity, "config")["description"] == details["description"]
            assert getattr(activity, "config")["schema"].json_schema("Schema") == details["schema"].json_schema(
                "Schema"
            )

            assert getattr(activity, "is_activity") is True

    def test_multiple_init(self, mock_schema):
        tool_1 = GriptapeCloudToolTool(tool_id="tool_id_1")
        mock_schema["paths"]["/activities/processString"]["post"]["description"] = "new description"
        tool_2 = GriptapeCloudToolTool(tool_id="tool_id_2")

        assert getattr(tool_1, "processString") != getattr(tool_2, "processString")
        assert getattr(tool_1, "processString").config["description"] == "Processes a string input"
        assert getattr(tool_2, "processString").config["description"] == "new description"

    def test_run_activity(self):
        tool = GriptapeCloudToolTool(tool_id="tool_id")
        response = tool.processString({"text": "foo"})  # pyright: ignore[reportAttributeAccessIssue]

        assert response.value == "foo"

    def test_name(self):
        tool = GriptapeCloudToolTool(tool_id="tool_id")

        assert tool.name == "DataProcessor"

        tool = GriptapeCloudToolTool(tool_id="tool_id", name="CustomName")

        assert tool.name == "CustomName"

    def test_bad_artifact(self, mocker):
        mock_get = mocker.patch("requests.post")
        mock_get.return_value.status_code = 200
        return_value = {"type": "FooBarArtifact", "value": "foo"}
        mock_get.return_value.json.return_value = return_value
        mock_get.return_value.text = json.dumps(return_value)
        tool = GriptapeCloudToolTool(tool_id="tool_id")

        result = tool.processString({"text": 1})
        assert isinstance(result, TextArtifact)
        assert result.value == json.dumps(return_value)
