from griptape.structures import Agent
from griptape.tasks import PromptTask

agent = Agent()
agent.add_task(
    # take the first argument from the agent `run` method
    PromptTask("Respond to the following request: {{ args[0] }}"),
)

agent.run("Write me a haiku")
