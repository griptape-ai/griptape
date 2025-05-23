import os

from griptape.drivers.prompt.amazon_sagemaker_jumpstart import AmazonSageMakerJumpstartPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=AmazonSageMakerJumpstartPromptDriver(
        endpoint=os.environ["SAGEMAKER_LLAMA_3_INSTRUCT_ENDPOINT_NAME"],
        model="meta-llama/Meta-Llama-3-8B-Instruct",
    )
)

agent.run("What is a good lasagna recipe?")
