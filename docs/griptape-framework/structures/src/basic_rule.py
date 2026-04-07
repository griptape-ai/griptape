from griptape.rules import Rule, Ruleset
from griptape.structures import Agent

pipeline = Agent(
    rulesets=[
        Ruleset(
            name="Personality",
            rules=[Rule("Talk like a pirate.")],
        ),
    ]
)

pipeline.run("Hi there! How are you?")
