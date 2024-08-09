from griptape.config import StructureConfig
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=AmazonBedrockPromptDriver(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
        )
    ),
    rules=[
        Rule(
            value="You are a customer service agent that is classifying emails by type. I want you to give your answer and then explain it."
        )
    ],
)
agent.run(
    """How would you categorize this email?
    <email>
    Can I use my Mixmaster 4000 to mix paint, or is it only meant for mixing food?
    </email>

    Categories are:
    (A) Pre-sale question
    (B) Broken or defective item
    (C) Billing question
    (D) Other (please explain)"""
)
