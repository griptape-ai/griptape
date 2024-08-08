from griptape.loaders import ImageLoader
from griptape.structures import Agent

agent = Agent()
with open("tests/resources/mountain.jpg", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

agent.run([image_artifact, "What's in this image?"])
