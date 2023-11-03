import pytest
from griptape.api import ToolApiGenerator
from griptape.api.extensions import ChatGptPluginApiExtension
from tests.mocks.mock_tool.tool import MockTool


class TestChatGptPluginApiExtension:
    @pytest.fixture
    def generator(self):
        return ToolApiGenerator(tool=MockTool())

    def test_generator_extension(self, generator):
        generator_with_extension = ToolApiGenerator(
            tool=MockTool(),
            extensions=[ChatGptPluginApiExtension()]
        )

        assert len(generator_with_extension.extensions[0].route_fns) == 2
        assert len(generator_with_extension.api.routes) - len(generator.api.routes) == 2

    def test_generate_manifest_route(self, generator):
        route = ChatGptPluginApiExtension().generate_manifest_route(generator)

        assert route["path"] == "/tools/chat_gpt_plugin_manifest.json.j2"
        assert isinstance(route["endpoint"](), dict)
        assert route["methods"] == ["GET"]
        assert route["operation_id"] == "OpenAPIManifest"
        assert route["description"] == "ChatGPT plugin manifest"

    def test_generate_spec_route(self, generator):
        route = ChatGptPluginApiExtension().generate_spec_route(generator)

        assert route["path"] == "/openapi.yaml"
        assert isinstance(route["endpoint"](), str)
        assert route["methods"] == ["GET"]
        assert str(route["response_class"]) == str(ChatGptPluginApiExtension.YAMLResponse)
        assert route["operation_id"] == "OpenAPISpec"
        assert route["description"] == "ChatGPT plugin spec"
