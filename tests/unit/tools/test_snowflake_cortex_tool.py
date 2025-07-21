import pytest

from griptape.artifacts import ErrorArtifact, JsonArtifact
from griptape.tools import SnowflakeCortexTool


class TestSnowflakeCortex:
    @pytest.fixture()
    def base_snowflake_cortex_tool(self, mocker):
        return SnowflakeCortexTool(
            account="test_account",
            user="test_user",
            password="test_password",
            role="test_role",
            search_service="sales_intelligence.data.sales_conversation_search",
            analyst_semantic_model_file="@sales_intelligence.data.models/sales_metrics_model.yaml",
        )

    @pytest.fixture()
    def snowflake_cortex_tool(self, mocker, base_snowflake_cortex_tool):
        mocker.patch.object(base_snowflake_cortex_tool, "snowflake_api_call", return_value=mocker.Mock())
        mocker.patch.object(
            base_snowflake_cortex_tool,
            "process_sse_response",
            return_value=("mock text", "", [{"source": "mock source"}]),
        )
        return base_snowflake_cortex_tool

    @pytest.fixture()
    def snowflake_cortex_tool_with_sql(self, mocker, base_snowflake_cortex_tool):
        mocker.patch.object(base_snowflake_cortex_tool, "snowflake_api_call", return_value=mocker.Mock())
        mocker.patch.object(
            base_snowflake_cortex_tool,
            "process_sse_response",
            return_value=("mock text", "mock sql", [{"source": "mock source"}]),
        )
        mocker.patch.object(base_snowflake_cortex_tool, "run_sql", return_value="mock sql result")
        return base_snowflake_cortex_tool

    @pytest.fixture()
    def snowflake_cortex_tool_with_error(self, mocker, base_snowflake_cortex_tool):
        mock_response = Exception("test_error")
        mocker.patch.object(base_snowflake_cortex_tool, "snowflake_api_call", side_effect=mock_response)
        return base_snowflake_cortex_tool

    def test_run_agent(self, snowflake_cortex_tool):
        result = snowflake_cortex_tool.run_agent({"values": {"prompt": "mock prompt"}})
        assert isinstance(result, JsonArtifact)
        assert result.value == {"text": "mock text"}

    def test_run_agent_with_sql(self, snowflake_cortex_tool_with_sql):
        result = snowflake_cortex_tool_with_sql.run_agent({"values": {"prompt": "mock prompt"}})
        assert isinstance(result, JsonArtifact)
        assert result.value == {"sql_result": "mock sql result", "text": "mock text"}

    def test_run_agent_with_error(self, snowflake_cortex_tool_with_error):
        result = snowflake_cortex_tool_with_error.run_agent({"values": {"prompt": "mock prompt"}})
        assert isinstance(result, ErrorArtifact)
        assert result.value == "Error running Snowflake Cortex agent: test_error"
