import os

from griptape.structures import Agent
from griptape.tools import OpenWeatherTool

agent = Agent(
    tools=[
        OpenWeatherTool(
            api_key=os.environ["OPENWEATHER_API_KEY"],
        ),
    ]
)

agent.run("What's the weather currently like in San Francisco?")
