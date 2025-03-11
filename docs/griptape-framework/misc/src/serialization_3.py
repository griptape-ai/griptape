from duckduckgo_search import DDGS
from rich.pretty import pprint

from griptape.drivers.web_search import BaseWebSearchDriver
from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver
from griptape.tools import WebSearchTool

web_driver = DuckDuckGoWebSearchDriver()
web_tool = WebSearchTool(web_search_driver=web_driver)

web_tool_dict = web_tool.to_dict(
    serializable_overrides={"web_search_driver": True},
    types_overrides={"BaseWebSearchDriver": BaseWebSearchDriver, "DDGS": DDGS},
)

pprint(web_tool_dict)
