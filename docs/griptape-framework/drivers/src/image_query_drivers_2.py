from griptape.drivers import AnthropicImageQueryDriver
from griptape.loaders import ImageLoader

driver = AnthropicImageQueryDriver(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
)

image_artifact1 = ImageLoader().load("tests/resources/mountain.png")

image_artifact2 = ImageLoader().load("tests/resources/cow.png")

result = driver.query("Describe the weather in the image", [image_artifact1, image_artifact2])

print(result)
