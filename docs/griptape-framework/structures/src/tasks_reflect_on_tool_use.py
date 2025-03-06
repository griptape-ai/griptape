from griptape.artifacts.list_artifact import ListArtifact
from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver
from griptape.tasks import PromptTask
from griptape.tools import WebScraperTool, WebSearchTool

search_task = PromptTask(
    tools=[WebSearchTool(web_search_driver=DuckDuckGoWebSearchDriver())],
    reflect_on_tool_use=False,
)
search_results = search_task.run("Do two searches, one for 'vim' and one for 'emacs'.")

# When disabling `reflect_on_tool_use`, the Task's results will be returned as a ListArtifact.
# Each item in the ListArtifact will be the result of a single tool execution.
if isinstance(search_results, ListArtifact):
    for result in search_results:
        print(result)

scrape_task = PromptTask(
    tools=[WebScraperTool()],
    reflect_on_tool_use=True,
)
# If we don't care about the individual results, we can join them back together before passing to the next task.
answer = scrape_task.run(["Compare and contrast vim and emacs: ", search_results.to_text()])
