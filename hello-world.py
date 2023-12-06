import random
from typing import cast
from griptape.drivers import OpenAiDalleImageGenerationDriver
from griptape.structures import Pipeline
from griptape.tools import WebScraper, FileManager
from griptape.tasks import ToolTask, TextSummaryTask, ImageGenerationTask
from griptape.engines import ImageGenerationEngine
from griptape.drivers import OpenAiChatPromptDriver
from griptape.artifacts import TextArtifact


def random_input(_):
    if random.random() < 0.5:
        return TextArtifact("Save the image artifact to a file called griptape_0.png in the images directory")
    else:
        return TextArtifact("Save the image artifact to a file called griptape_1.png in the images directory")


pipeline = Pipeline(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    tasks=[
        ToolTask("Scrape https://griptape.ai", tool=WebScraper(), id="WebResults"),
        TextSummaryTask(lambda task: cast(TextArtifact, task.parents[0].output), id="WebSummary"),
        ImageGenerationTask(
            lambda _: cast(TextArtifact, pipeline.find_task("WebSummary").output),
            id="ImageGeneration",
            image_generation_engine=ImageGenerationEngine(
                image_generation_driver=OpenAiDalleImageGenerationDriver(model="dall-e-3")
            ),
        ),
        ToolTask(random_input, tool=FileManager()),
    ],
)

pipeline.run()
