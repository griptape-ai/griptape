import schema

from griptape.engines import JsonExtractionEngine
from griptape.structures import Agent
from griptape.tools import ExtractionClient, WebScraper

agent = Agent(
    input="Load {{ args[0] }} and extract key info",
    tools=[
        WebScraper(off_prompt=True),
        ExtractionClient(
            off_prompt=False,
            extraction_engine=JsonExtractionEngine(
                template_schema=schema.Schema(
                    {
                        "company_name": str,
                        "industry": str,
                        schema.Literal(
                            "product_features",
                            description="List of key product features.",
                        ): list[str],
                    }
                ).json_schema("Company Info"),
            ),
        ),
    ],
)
agent.run("https://griptape.ai")
