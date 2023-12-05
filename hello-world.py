import random
from griptape.drivers import OpenAiDalleImageGenerationDriver
from griptape.structures import Pipeline
from griptape.tools import WebScraper, FileManager
from griptape.tasks import ToolTask, TextSummaryTask, ImageGenerationTask
from griptape.engines import ImageGenerationEngine
from griptape.drivers import OpenAiChatPromptDriver


def random_input():
    if random.random() < 0.5:
        return "Save the image artifact to a file called griptape_0.png in the images directory"
    else:
        return "Save the image artifact to a file called griptape_1.png in the images directory"


pipeline = Pipeline(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    tasks=[
        ToolTask("Scrape https://griptape.ai", tool=WebScraper(), id="WebResults"),
        TextSummaryTask(input_generator_fn=lambda: pipeline.find_task("WebResults"), off_prompt=True, id="WebSummary"),
        ImageGenerationTask(
            id="ImageGeneration",
            input_generator_fn=lambda: pipeline.find_task("WebSummary"),
            image_generation_engine=ImageGenerationEngine(
                image_generation_driver=OpenAiDalleImageGenerationDriver(model="dall-e-3")
            ),
            off_prompt=True,
        ),
        ToolTask(input_generator_fn=random_input, off_prompt=False, tool=FileManager()),
    ],
)

pipeline.run()
