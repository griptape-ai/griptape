from griptape.configs import Defaults
from griptape.configs.drivers import AnthropicDriversConfig, OpenAiDriversConfig
from griptape.drivers.prompt.anthropic_prompt_driver import AnthropicPromptDriver
from griptape.structures import Agent

Defaults.drivers_config = OpenAiDriversConfig()  # Default
openai_agent = Agent()

Defaults.drivers_config = AnthropicDriversConfig()
anthropic_agent = Agent(
    prompt_driver=AnthropicPromptDriver(model="claude-3-5-sonnet-20240620"),  # Override the default prompt driver
)
