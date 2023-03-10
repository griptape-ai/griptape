from attrs import define, field
from warpspeed.tools import Tool
from sqlalchemy import create_engine, text


@define
class SqlClientTool(Tool):
    engine_url: str = field(kw_only=True)
    engine_hint: str = field(kw_only=True)

    def run(self, query: str) -> str:
        engine = create_engine(self.engine_url)

        try:
            with engine.connect() as con:
                results = con.execute(text(query))

                if results.returns_rows:
                    return str([row for row in results]).strip('[]')
                else:
                    return "query successfully executed"

        except Exception as e:
            return f"error executing SQL: {e}"

    @property
    def schema_kwargs(self) -> dict:
        return {
            "engine": self.engine_hint
        }
