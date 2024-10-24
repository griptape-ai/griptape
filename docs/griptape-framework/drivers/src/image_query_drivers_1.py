from griptape.drivers import AnthropicImageQueryDriver
from griptape.loaders import ImageLoader

driver = AnthropicImageQueryDriver(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
)


image_artifact = ImageLoader().load("tests/resources/mountain.png")

driver.query("Describe the weather in the image", [image_artifact])
