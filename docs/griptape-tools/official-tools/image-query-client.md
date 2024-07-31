# ImageQueryClient

This tool allows Agents to execute natural language queries on the contents of images using multimodal models.

```python
from griptape.structures import Agent
from griptape.tools import ImageQueryClient
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import ImageQueryEngine

# Create an Image Query Driver.
driver = OpenAiImageQueryDriver(
    model="gpt-4o"
)

# Create an Image Query Client configured to use the engine.
tool = ImageQueryClient(
    prompt_driver=engine,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run("Describe the weather in the image tests/resources/mountain.png in one word.")
```
