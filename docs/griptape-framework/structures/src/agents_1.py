from griptape.structures import Agent

agent = Agent(
    input="Write me a {{ args[0] }} about {{ args[1] }} and {{ args[2] }}",
)

agent.run("Haiku", "Skateboards", "Programming")
