# SqlClientTool

This tool enables LLMs to execute SQL statements via [SQLAlchemy](https://www.sqlalchemy.org/). Depending on your underlying SQL engine, [configure](https://docs.sqlalchemy.org/en/20/core/engines.html) your `engine_url` and give the LLM a hint about what engine you are using via `engine_hint`, so that it can create engine-specific statements.

```python
ToolStep(
    "list the last 20 items in the orders table",
    tool=SqlClientTool(
        engine_url="sqlite:///warpspeed.db",
        engine_hint="sqlite"
    )
)
```