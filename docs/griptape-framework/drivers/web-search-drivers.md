---
search:
  boost: 2 
---

## Overview

Web Search Drivers can be used to search for links from a search query. They are used by [WebSearch](../../reference/griptape/tools/web_search/tool.md) to provide its functionality. All Web Search Drivers implement the following methods:

* `search()` searches the web and returns a [ListArtifact](../../reference/griptape/artifacts/list_artifact.md) that contains JSON-serializable [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s with the search results.

## Vector Store Drivers

### Google

The [GoogleWebSearchDriver](../../reference/griptape/drivers/web_search/google_web_search_driver.md) uses the [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list) for web searching.

Example using `GoogleWebSearchDriver` directly:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_1.py"
```

Example of using `GoogleWebSearchDriver` with an agent:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_2.py"
```

### DuckDuckGo

!!! info
    This driver requires the `drivers-web-search-duckduckgo` [extra](../index.md#extras).

The [DuckDuckGoWebSearchDriver](../../reference/griptape/drivers/web_search/duck_duck_go_web_search_driver.md) uses the [duckduckgo_search](https://github.com/deedy5/duckduckgo_search) SDK for web searching.

Example of using `DuckDuckGoWebSearchDriver` directly:

```python
--8<-- "docs/griptape-framework/drivers/src/web_search_drivers_3.py"
```
