from pathlib import Path

from griptape.drivers import OpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = OpenAiImageQueryDriver(
    model="gpt-4o",
    max_tokens=256,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

engine.run("Describe the weather in the image", [image_artifact])
