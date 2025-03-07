from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver
from griptape.tasks import PromptTask
from griptape.tools import WebScraperTool, WebSearchTool

search_task = PromptTask(
    tools=[WebSearchTool(web_search_driver=DuckDuckGoWebSearchDriver())],
    reflect_on_tool_use=False,
)
search_results = search_task.run("Do two searches, one for 'vim' and one for 'emacs'.")

scrape_task = PromptTask(
    tools=[WebScraperTool()],
    reflect_on_tool_use=True,
)
answer = scrape_task.run(["Compare and contrast vim and emacs:", search_results.to_text()])
