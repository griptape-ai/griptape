from pathlib import Path

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

image_artifact1 = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

image_artifact2 = ImageLoader().load(Path("tests/resources/cow.png").read_bytes())

result = engine.run("Describe the weather in the image", [image_artifact1, image_artifact2])

print(result)
