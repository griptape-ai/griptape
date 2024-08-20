from griptape.rules import Rule, Ruleset
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    rulesets=[
        Ruleset(
            name="Employment",
            rules=[
                Rule("Behave like a polite customer support agent"),
                Rule("Act like you work for company SkaterWorld, Inc."),
                Rule("Discuss only topics related to skateboarding"),
                Rule("Limit your response to fewer than 5 sentences."),
            ],
        ),
        Ruleset(
            name="Background",
            rules=[
                Rule("Your name is Todd"),
            ],
        ),
    ]
)

pipeline.add_tasks(
    PromptTask(input="Respond to this user's question: {{ args[0] }}"),
    PromptTask(input="Extract keywords from this response: {{ parent_output }}"),
)

pipeline.run("How do I do a kickflip?")
