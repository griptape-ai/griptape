import os

from griptape.drivers.web_search.google import GoogleWebSearchDriver
from griptape.structures import Agent
from griptape.tools import WebSearchTool

# Initialize the WebSearchTool tool with necessary parameters
web_search_tool = WebSearchTool(
    web_search_driver=GoogleWebSearchDriver(
        api_key=os.environ["GOOGLE_API_KEY"],
        search_id=os.environ["GOOGLE_API_SEARCH_ID"],
        results_count=5,
        language="en",
        country="us",
    ),
)

# Set up an agent using the WebSearchTool tool
agent = Agent(tools=[web_search_tool])

# Task: Search the web for a specific query
agent.run("Tell me how photosynthesis works")
