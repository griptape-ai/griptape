from griptape.drivers import OpenAiImageGenerationDriver
from griptape.structures import Pipeline
from griptape.tasks import PromptImageGenerationTask

# Create a driver configured to use OpenAI's DALL-E 3 model.
driver = OpenAiImageGenerationDriver(
    model="dall-e-3",
    quality="hd",
    style="natural",
)


# Instantiate a pipeline.
pipeline = Pipeline()

# Add a PromptImageGenerationTask to the pipeline.
pipeline.add_tasks(
    PromptImageGenerationTask(
        input="{{ args[0] }}",
        image_generation_driver=driver,
        output_dir="images/",
    )
)

pipeline.run("An image of a mountain on a summer day")
