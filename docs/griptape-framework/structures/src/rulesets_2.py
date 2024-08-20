from griptape.rules import Rule
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    rules=[
        Rule("Respond only using emojis"),
    ],
)

pipeline.add_tasks(
    PromptTask("Respond to this question from the user: '{{ args[0] }}'"),
    PromptTask("How would you rate your response (1-5)? 1 being bad, 5 being good. Response: '{{parent_output}}'"),
)

pipeline.run("How do I bake a cake?")
