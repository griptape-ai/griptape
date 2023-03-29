# WikiTool

This tool enables LLMs to search and query Wikipedia articles:

```python
ToolStep(
    "Research and summarize biggest world news stories in February of 2023",
    tool=WikiTool()
)
```