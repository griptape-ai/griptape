from griptape.drivers.image_generation.openai import OpenAiImageGenerationDriver
from griptape.structures import Agent
from griptape.tools import FileManagerTool, PromptImageGenerationTool

driver = OpenAiImageGenerationDriver(model="gpt-image-1")

agent = Agent(tools=[PromptImageGenerationTool(image_generation_driver=driver, off_prompt=True), FileManagerTool()])

agent.run("Generate a watercolor painting of a dog riding a skateboard and save it to dog.png")
