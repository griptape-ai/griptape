from griptape.config import StructureConfig
from griptape.drivers import HuggingFacePipelinePromptDriver
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFacePipelinePromptDriver(
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        )
    ),
    rulesets=[
        Ruleset(
            name="Pirate",
            rules=[Rule(value="You are a pirate chatbot who always responds in pirate speak!")],
        )
    ],
)

agent.run("How many helicopters can a human eat in one sitting?")
