from griptape.drivers import OpenAiChatPromptDriver
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import ImageQueryTask

# Create a driver configured to use OpenAI's GPT-4 Vision model.
driver = OpenAiChatPromptDriver(
    model="gpt-4o",
    max_tokens=100,
)


# Load the input image artifact.
image_artifact = ImageLoader().load("tests/resources/mountain.png")

# Instantiate a pipeline.
pipeline = Pipeline()

# Add an ImageQueryTask to the pipeline.
pipeline.add_task(
    ImageQueryTask(
        input=("{{ args[0] }}", [image_artifact]),
        prompt_driver=driver,
    )
)

pipeline.run("Describe the weather in the image")
