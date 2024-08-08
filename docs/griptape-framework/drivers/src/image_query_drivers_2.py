from griptape.drivers import AnthropicImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = AnthropicImageQueryDriver(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact1 = ImageLoader().load(f.read())

with open("tests/resources/cow.png", "rb") as f:
    image_artifact2 = ImageLoader().load(f.read())

result = engine.run("Describe the weather in the image", [image_artifact1, image_artifact2])

print(result)
