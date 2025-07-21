from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, JsonArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from snowflake.core.rest import SSEClient

API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 30000  # in milliseconds


@define
class SnowflakeCortexTool(BaseTool):
    """Snowflake Cortex activities through a tool.

    Requires Python 3.10 or higher due to Snowflake dependencies.

    Attributes:
        account: Snowflake account name.
        user: Snowflake user name.
        password: Snowflake user password.
        role: Snowflake role.
        agent_model: Snowflake Cortex Agent model to use. ex: "claude-3-5-sonnet"
        search_limit: Maximum number of Cortex Search results to return. Default is 10.
        search_service: Snowflake Cortex Search service name. ex: "sales_intelligence.data.sales_conversation_search"
        analyst_semantic_model_file: Snowflake Analyst semantic model file. ex: "@sales_intelligence.data.models/sales_metrics_model.yaml"
    """

    account: str = field(kw_only=True)
    user: str = field(kw_only=True)
    password: str = field(kw_only=True)
    role: str = field(kw_only=True)
    agent_model: str = field(default="claude-3-5-sonnet", kw_only=True)
    search_limit: int = field(default=10, kw_only=True)
    search_service: str = field(kw_only=True)
    analyst_semantic_model_file: str = field(kw_only=True)
    description: str = field(default="Natural language searches and SQL generation", kw_only=True)

    def snowflake_api_call(self, query: str) -> SSEClient:
        from snowflake.core import Root
        from snowflake.core.cortex.lite_agent_service import AgentRunRequest, CortexAgentService
        from snowflake.snowpark import Session  # pyright: ignore[reportMissingImports]

        payload = {
            "model": self.agent_model,
            "messages": [{"role": "user", "content": [{"type": "text", "text": query}]}],
            "tools": [
                {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "analyst"}},
                {"tool_spec": {"type": "cortex_search", "name": "search"}},
            ],
            "tool_resources": {
                "analyst": {"semantic_model_file": self.analyst_semantic_model_file},
                "search": {
                    "name": self.search_service,
                    "max_results": self.search_limit,
                    "id_column": "conversation_id",
                },
            },
        }

        session = Session.builder.configs(
            {
                "account": self.account,
                "user": self.user,
                "password": self.password,
                "role": self.role,
            }
        ).create()
        root = Root(session)
        cortex_agent_service = CortexAgentService(root)
        op = cortex_agent_service.run_async(AgentRunRequest(**payload))
        return op.result()

    def process_sse_response(self, client: SSEClient) -> tuple[str, str, list[dict]]:
        text = ""
        sql = ""
        citations = []

        for event in client.events():
            if event.event == "message.delta":
                data = event.data if hasattr(event, "data") and event.data else ""
                delta = json.loads(data).get("delta", {})

                for content_item in delta.get("content", []):
                    content_type = content_item.get("type")
                    if content_type == "tool_results":
                        tool_results = content_item.get("tool_results", {})
                        if "content" in tool_results:
                            for result in tool_results["content"]:
                                if result.get("type") == "json":
                                    text += result.get("json", {}).get("text", "")
                                    search_results = result.get("json", {}).get("searchResults", [])
                                    for search_result in search_results:
                                        citations.append(
                                            {
                                                "source_id": search_result.get("source_id", ""),
                                                "doc_id": search_result.get("doc_id", ""),
                                            }
                                        )
                                    sql = result.get("json", {}).get("sql", "")
                    if content_type == "text":
                        text += content_item.get("text", "")

        return text, sql, citations

    def run_sql(self, sql: str) -> list:
        import snowflake.connector

        conn = snowflake.connector.connect(user=self.user, password=self.password, account=self.account, role=self.role)
        cur = conn.cursor()
        cur.execute(sql)
        if cur.sfqid is None:
            raise Exception("SQL execution failed")
        cur.get_results_from_sfqid(cur.sfqid)
        return cur.fetchall()

    @activity(
        config={
            "description": "{{ _self.description }}",
            "schema": Schema(
                {Literal("prompt", description="Natural language prompt to send to the Snowflake Cortex Agent"): str},
            ),
        },
    )
    def run_agent(self, params: dict) -> JsonArtifact | ErrorArtifact:
        try:
            client = self.snowflake_api_call(params["values"]["prompt"])
            text, sql, citations = self.process_sse_response(client)
            if sql:
                sql_result = self.run_sql(sql)
                return JsonArtifact(
                    value={"text": text, "sql_result": sql_result},
                    meta={"citations": citations, "sql": sql},
                )
            return JsonArtifact(value={"text": text}, meta={"citations": citations})
        except Exception as e:
            return ErrorArtifact(value=f"Error running Snowflake Cortex agent: {e}")
