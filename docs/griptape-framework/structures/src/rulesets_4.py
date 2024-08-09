from griptape.rules import Rule
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline()

pipeline.add_tasks(
    PromptTask(
        rules=[
            Rule("Write your answer in json with a single key 'emoji_response'"),
            Rule("Respond only using emojis"),
        ],
    ),
)

pipeline.run("How are you?")
