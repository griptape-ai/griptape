# GoogleSearchTool

This tool enables LLMs to search Google. Every search returns links, titles, and short descriptions. Search has two modes: scraping (default) and API-based. To enable [API-based search](https://programmablesearchengine.google.com) set `use_api`, `api_search_key`, and `api_search_id` params.

```python
ToolStep(
    "Find the latest on LLMs",
    tool=GoogleSearchTool()
)
```