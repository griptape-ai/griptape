from griptape.loaders import ImageLoader
from griptape.structures import Agent

agent = Agent()

image_artifact = ImageLoader().load("tests/resources/mountain.jpg")

agent.run([image_artifact, "What's in this image?"])
