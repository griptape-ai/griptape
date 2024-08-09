from griptape.config import OpenAiStructureConfig
from griptape.structures import Agent

agent = Agent(config=OpenAiStructureConfig())

agent = Agent()  # This is equivalent to the above
