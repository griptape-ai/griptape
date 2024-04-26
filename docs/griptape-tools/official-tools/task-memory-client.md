# TaskMemoryClient

This tool enables LLMs to query and summarize task outputs that are stored in short-term tool memory. This tool uniquely requires the user to set the `off_prompt` property explicitly for usability reasons (Griptape doesn't provide the default `True` value).

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, TaskMemoryClient


Agent(tools=[WebScraper(), TaskMemoryClient(off_prompt=False)])
```
