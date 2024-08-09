from pathlib import Path

from griptape.loaders import ImageLoader
from griptape.structures import Agent

agent = Agent()

image_artifact = ImageLoader().load(Path("tests/resources/mountain.jpg").read_bytes())

agent.run([image_artifact, "What's in this image?"])
