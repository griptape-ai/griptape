import os

from griptape.drivers.prompt.huggingface_hub import HuggingFaceHubPromptDriver
from griptape.loaders import ImageLoader
from griptape.structures import Agent

agent = Agent(
    prompt_driver=HuggingFaceHubPromptDriver(
        model="Qwen/Qwen3.5-9B",
        api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
        max_tokens=2000,
    ),
)

image_artifact = ImageLoader().load("./tests/resources/mountain.jpg")

agent.run(["Describe the weather in the image", image_artifact])
