import pytest
from fastapi import FastAPI
from griptape.core.adapters import ChatgptPluginAdapter
from griptape.core.executors import LocalExecutor
from tests.mocks.mock_tool.tool import MockTool


class TestChatgptPluginAdapter:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello"
        )

    @pytest.fixture
    def executor(self):
        return LocalExecutor()

    def test_full_host(self, tool, executor):
        assert ChatgptPluginAdapter(executor=executor, host="foo", path_prefix="/bar").full_host == "foo/bar"

    def test_generate_manifest(self, tool, executor):
        adapter = ChatgptPluginAdapter(executor=executor, host="foo")
        manifest = adapter.generate_manifest(tool)

        assert manifest["schema_version"] == "v1"
        assert manifest["name_for_human"] == tool.manifest["name"]
        assert manifest["name_for_model"] == tool.manifest["name"]
        assert manifest["description_for_human"] == tool.manifest["description"]
        assert manifest["description_for_model"] == tool.manifest["description"]
        assert manifest["auth"]["type"] == "none"
        assert manifest["api"]["type"] == "openapi"
        assert manifest["api"]["url"] == f"{adapter.full_host}{adapter.OPENAPI_SPEC_FILE}"
        assert manifest["api"]["is_user_authenticated"] is False
        assert manifest["logo_url"] == f"{adapter.full_host}logo.png"
        assert manifest["contact_email"] == tool.manifest["contact_email"]
        assert manifest["legal_info_url"] == tool.manifest["legal_info_url"]

    def test_generate_api_spec(self, tool, executor):
        adapter = ChatgptPluginAdapter(executor=executor, host="foo")
        api = adapter.generate_api(tool)

        assert isinstance(adapter.generate_api_spec(api), str)

    def test_generate_api(self, tool, executor):
        adapter = ChatgptPluginAdapter(executor=executor, host="foo")
        assert isinstance(adapter.generate_api(tool), FastAPI)