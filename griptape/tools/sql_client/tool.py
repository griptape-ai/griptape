from __future__ import annotations
from typing import Optional
from attr import define, field
from griptape.artifacts import InfoArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.loaders import SqlLoader
from schema import Schema


@define
class SqlClient(BaseTool):
    sql_loader: SqlLoader = field(kw_only=True)
    schema_name: str | None = field(default=None, kw_only=True)
    table_name: str = field(kw_only=True)
    table_description: str | None = field(default=None, kw_only=True)
    engine_name: str | None = field(default=None, kw_only=True)

    @property
    def full_table_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}" if self.schema_name else self.table_name

    @property
    def table_schema(self) -> str:
        return self.sql_loader.sql_driver.get_table_schema(self.full_table_name, schema=self.schema_name)

    @activity(
        config={
            "description": "Can be used to execute{% if _self.engine_name %} {{ _self.engine_name }}{% endif %} SQL SELECT queries "
            "in table {{ _self.full_table_name }}. "
            "Make sure the `SELECT` statement contains enough columns to get an answer without knowing "
            "the original question. "
            "Be creative when you use `WHERE` statements: you can use wildcards, `LOWER()`, and other functions "
            "to get better results. "
            "You can use JOINs if more tables are available in other tools.\n"
            "{{ _self.table_name }} schema: {{ _self.table_schema }}\n"
            "{% if _self.table_description %}{{ _self.table_name }} description: {{ _self.table_description }}{% endif %}",
            "schema": Schema({"sql_query": str}),
        }
    )
    def execute_query(self, params: dict) -> ListArtifact | InfoArtifact:
        query = params["values"]["sql_query"]
        rows = self.sql_loader.load(query)

        if len(rows) > 0:
            return ListArtifact(rows)
        else:
            return InfoArtifact("No results found")
