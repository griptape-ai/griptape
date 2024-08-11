import os

from griptape.config import StructureConfig
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFaceHubPromptDriver(
            model="HuggingFaceH4/zephyr-7b-beta",
            api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
        )
    ),
    rulesets=[
        Ruleset(
            name="Girafatron",
            rules=[
                Rule(
                    value="You are Girafatron, a giraffe-obsessed robot. You are talking to a human. "
                    "Girafatron is obsessed with giraffes, the most glorious animal on the face of this Earth. "
                    "Giraftron believes all other animals are irrelevant when compared to the glorious majesty of the giraffe."
                )
            ],
        )
    ],
)

agent.run("Hello Girafatron, what is your favorite animal?")
