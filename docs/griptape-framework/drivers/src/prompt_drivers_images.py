from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.loaders import ImageLoader

driver = OpenAiChatPromptDriver(model="gpt-4o", max_tokens=256)

image_artifact = ImageLoader().load("./tests/resources/mountain.jpg")
text_artifact = TextArtifact("Describe the weather in the image")

driver.run(ListArtifact([text_artifact, image_artifact]))
