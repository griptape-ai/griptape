from griptape.drivers.prompt.anthropic import AnthropicPromptDriver
from griptape.tasks import PromptTask

task = PromptTask(prompt_driver=AnthropicPromptDriver(model="claude-3-7-sonnet-latest"))

task.run("Hello there!")
