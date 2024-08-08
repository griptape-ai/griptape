import os

from griptape.drivers import AzureOpenAiImageGenerationDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient

driver = AzureOpenAiImageGenerationDriver(
    model="dall-e-3",
    azure_deployment=os.environ["AZURE_OPENAI_DALL_E_3_DEPLOYMENT_ID"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_2"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_2"],
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(
    tools=[
        PromptImageGenerationClient(engine=engine),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
