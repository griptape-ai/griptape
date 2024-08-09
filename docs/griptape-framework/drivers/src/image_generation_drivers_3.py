from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockTitanImageGenerationModelDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient

model_driver = BedrockTitanImageGenerationModelDriver()

driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=model_driver,
    model="amazon.titan-image-generator-v1",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(
    tools=[
        PromptImageGenerationClient(engine=engine),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
