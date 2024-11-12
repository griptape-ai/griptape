from griptape.drivers import OpenAiImageQueryDriver
from griptape.loaders import ImageLoader

driver = OpenAiImageQueryDriver(
    model="gpt-4o",
    max_tokens=256,
)

image_artifact = ImageLoader().load("tests/resources/mountain.png")

driver.query("Describe the weather in the image", [image_artifact])
