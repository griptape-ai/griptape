## Overview

Web Search Drivers can be used to search for links from a search query. They are used by [WebSearch](../../reference/griptape/tools/web_search/tool.md) to provide its functionality. All Web Search Drivers implement the following methods:

* `search()` searches the web and returns a [ListArtifact](../../reference/griptape/artifacts/list_artifact.md) that contains JSON-serializable [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s with the search results.

## Google

The [GoogleWebSearchDriver](../../reference/griptape/drivers/web_search/google_web_search_driver.md) uses the [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list) for web searching.

Example using `GoogleWebSearchDriver` directly:

```python
import os
from griptape.drivers import GoogleWebSearchDriver

driver = GoogleWebSearchDriver(
    api_key=os.environ["GOOGLE_API_KEY"],
    search_id=os.environ["GOOGLE_API_SEARCH_ID"],
)

driver.search("griptape ai")
```

Example of using `GoogleWebSearchDriver` with an agent:

```python
import os
from griptape.drivers import GoogleWebSearchDriver
from griptape.tools import TaskMemoryClient, WebSearch
from griptape.structures import Agent

agent = Agent(
    tools=[
        WebSearch(
            web_search_driver=GoogleWebSearchDriver(
                api_key=os.environ["GOOGLE_API_KEY"],
                search_id=os.environ["GOOGLE_API_SEARCH_ID"],
            ),
        ),
        TaskMemoryClient(off_prompt=False),
    ],
)
agent.run("Give me some websites with information about AI frameworks.")
```

## DuckDuckGo

!!! info
    This driver requires the `drivers-web-search-duckduckgo` [extra](../index.md#extras).

The [DuckDuckGoWebSearchDriver](../../reference/griptape/drivers/web_search/duck_duck_go_web_search_driver.md) uses the [duckduckgo_search](https://github.com/deedy5/duckduckgo_search) SDK for web searching.

Example of using `DuckDuckGoWebSearchDriver` directly:

```python
from griptape.drivers import DuckDuckGoWebSearchDriver

driver = DuckDuckGoWebSearchDriver()

driver.search("griptape ai")
```
