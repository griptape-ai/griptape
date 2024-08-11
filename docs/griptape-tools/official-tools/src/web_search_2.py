import os

import schema

from griptape.drivers import GoogleWebSearchDriver
from griptape.structures import Agent
from griptape.tools import WebSearch

agent = Agent(
    tools=[
        WebSearch(
            web_search_driver=GoogleWebSearchDriver(
                api_key=os.environ["GOOGLE_API_KEY"],
                search_id=os.environ["GOOGLE_API_SEARCH_ID"],
            ),
            extra_schema_properties={
                "search": {
                    schema.Literal(
                        "sort",
                        description="Date range to search within. Format: date:r:YYYYMMDD:YYYYMMDD",
                    ): str
                }
            },
        )
    ],
)

agent.run("Search for articles about the history of the internet from 1990 to 2000")
