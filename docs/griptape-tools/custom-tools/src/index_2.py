from rng_tool.tool import RandomNumberGenerator

from griptape.structures import Agent

rng_tool = RandomNumberGenerator()

agent = Agent(tools=[rng_tool])

agent.run("generate a random number rounded to 5 decimal places")
