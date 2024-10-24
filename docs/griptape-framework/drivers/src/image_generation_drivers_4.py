import os

from griptape.drivers import AzureOpenAiImageGenerationDriver
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationTool

driver = AzureOpenAiImageGenerationDriver(
    model="dall-e-3",
    azure_deployment=os.environ["AZURE_OPENAI_DALL_E_3_DEPLOYMENT_ID"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_2"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_2"],
)


agent = Agent(
    tools=[
        PromptImageGenerationTool(image_generation_driver=driver),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
