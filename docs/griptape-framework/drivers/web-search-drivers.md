---
search:
  boost: 2
---

## Overview

Web Search Drivers can be used to search for links from a search query. They are used by [WebSearch](../../reference/griptape/tools/web_search/tool.md) to provide its functionality. All Web Search Drivers implement the following methods:

* `search()` searches the web and returns a [ListArtifact](../../reference/griptape/artifacts/list_artifact.md) that contains JSON-serializable [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s with the search results.

You can use Web Search Drivers with structures:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_5.py"
```
Or use them independently:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_3.py"
```


## Web Search Drivers

### Google

The [GoogleWebSearchDriver](../../reference/griptape/drivers/web_search/google_web_search_driver.md) uses the [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list) for web searching.

Example using `GoogleWebSearchDriver` directly:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_1.py"
```

### DuckDuckGo

!!! info
    This driver requires the `drivers-web-search-duckduckgo` [extra](../index.md#extras).

The [DuckDuckGoWebSearchDriver](../../reference/griptape/drivers/web_search/duck_duck_go_web_search_driver.md) uses the [duckduckgo_search](https://github.com/deedy5/duckduckgo_search) SDK for web searching.

Example of using `DuckDuckGoWebSearchDriver` directly:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_3.py"
```

### Tavily
!!! info
    This driver requires the `drivers-web-search-tavily` [extra](../index.md#extras), and a Tavily [API-KEY](https://app.tavily.com).

The [TavilyWebSearchDriver](../../reference/griptape/drivers/web_search/tavily_web_search_driver.md) uses the [tavily-python](https://github.com/tavily-ai/tavily-python) SDK for web searching.

Example of using `TavilyWebSearchDriver` directly:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_4.py"
```