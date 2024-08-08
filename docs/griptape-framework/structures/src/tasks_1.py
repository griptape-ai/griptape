from griptape.structures import Agent
from griptape.tasks import PromptTask

agent = Agent()
agent.add_task(
    PromptTask(
        "Respond to the user's following question '{{ args[0] }}' in the language '{{preferred_language}}' and tone '{{tone}}'.",
        context={"preferred_language": "ENGLISH", "tone": "PLAYFUL"},
    )
)

agent.run("How do I bake a cake?")
