import json
import pytest
from griptape.api import ToolApiGenerator
from griptape.artifacts import BaseArtifact
from tests.mocks.mock_tool.tool import MockTool


class TestToolApiGenerator:
    @pytest.fixture
    def generator(self):
        return ToolApiGenerator(tool=MockTool())

    def test_generate_yaml_api_spec(self, generator):
        spec = generator.generate_yaml_api_spec()

        assert spec.startswith(
            "components:\n  schemas:\n    HTTPValidationError"
        )
        assert "test" in spec
        assert "test-error" in spec
        assert "test-str-output" in spec
        assert spec.endswith(
            "description: Validation Error\n      summary: Execute Activity\n"
        )

    def test_generate_json_api_spec(self, generator):
        spec = generator.generate_json_api_spec()

        assert spec.startswith(
            '{"openapi": "3.1.0", "info": {"title": "MockTool API"'
        )
        assert "test" in spec
        assert "test-error" in spec
        assert "test-str-output" in spec
        assert spec.endswith(
            '"required": ["loc", "msg", "type"], "title": "ValidationError"}}}}'
        )

    def test_generate_api(self, generator):
        api = generator.generate_api()

        assert api.title == "MockTool API"
        assert len(api.routes) == 10

    def test_execute_activity_fn(self, generator):
        activity = generator.tool.test

        assert (
            BaseArtifact.from_dict(
                generator.execute_activity_fn(activity)(
                    json.dumps({"values": {"test": "foobar"}})
                )
            ).value
            == "ack foobar"
        )
