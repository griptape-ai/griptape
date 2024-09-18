import schema

from griptape.configs.drivers import AnthropicDriversConfig, OpenAiDriversConfig
from griptape.drivers import AnthropicPromptDriver, OpenAiChatPromptDriver
from griptape.engines import JsonExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ToolTask
from griptape.tools import ExtractionTool

with OpenAiDriversConfig():  # Agent will be created with OpenAi Drivers
    openai_agent = Agent()

with AnthropicDriversConfig():  # Agent will be created with Anthropic Drivers
    anthropic_agent = Agent(
        tasks=[
            ToolTask(
                "Extract sentiment from this text: {{ args[0] }}",
                prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),  # Override this particular Task's prompt driver
                tool=ExtractionTool(
                    extraction_engine=JsonExtractionEngine(
                        prompt_driver=AnthropicPromptDriver(  # Override this particular Engine's prompt driver
                            model="claude-3-opus-20240229"
                        ),
                        template_schema=schema.Schema({"sentiment": str}).json_schema("Output"),
                    ),
                ),
            )
        ]
    )

anthropic_agent.run("Hello, I am happy!")
