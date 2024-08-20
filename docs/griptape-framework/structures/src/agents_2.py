from griptape.structures import Agent
from griptape.tasks import PromptTask

agent = Agent()
agent.add_task(
    PromptTask(
        "Write me a {{ creative_medium }} about {{ args[0] }} and {{ args[1] }}", context={"creative_medium": "haiku"}
    )
)

agent.run("Skateboards", "Programming")
