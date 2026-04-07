from griptape.rules import Rule, Ruleset
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline()

pipeline.add_tasks(
    PromptTask(
        input="Respond to the following prompt: {{ args[0] }}",
        rulesets=[
            Ruleset(
                name="Emojis",
                rules=[
                    Rule("Respond using uppercase characters only."),
                ],
            )
        ],
    ),
    PromptTask(
        input="Determine the sentiment of the following text: {{ parent_output }}",
        rulesets=[
            Ruleset(
                name="Diacritic",
                rules=[
                    Rule("Respond using diacritic characters only."),
                ],
            )
        ],
    ),
)

pipeline.run("I love skateboarding!")
