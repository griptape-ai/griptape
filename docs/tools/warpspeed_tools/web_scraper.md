# WebScraperTool

This tool enables LLMs to scrape web pages for full text, summaries, authors, titles, and keywords. It can also execute search queries to answer specific questions about the page.

```python
ToolStep(
    "Can you tell me what's on this page? https://github.com/usewarpspeed/warpspeed",
    tool=WebScraperTool()
)
```