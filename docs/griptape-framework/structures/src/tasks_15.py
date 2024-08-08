from pathlib import Path

from griptape.drivers import OpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import ImageQueryTask

# Create a driver configured to use OpenAI's GPT-4 Vision model.
driver = OpenAiImageQueryDriver(
    model="gpt-4o",
    max_tokens=100,
)

# Create an engine configured to use the driver.
engine = ImageQueryEngine(
    image_query_driver=driver,
)

# Load the input image artifact.
image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

# Instantiate a pipeline.
pipeline = Pipeline()

# Add an ImageQueryTask to the pipeline.
pipeline.add_task(
    ImageQueryTask(
        input=("{{ args[0] }}", [image_artifact]),
        image_query_engine=engine,
    )
)

pipeline.run("Describe the weather in the image")
