from griptape.drivers import OpenAiDalleImageGenerationDriver
from griptape.structures import Pipeline
from griptape.tools import WebScraper, FileManager
from griptape.tasks import ToolTask, TextSummaryTask, ImageGenerationTask
from griptape.engines import ImageGenerationEngine
from griptape.drivers import OpenAiChatPromptDriver

pipeline = Pipeline(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    tasks=[
        ToolTask("Scrape https://griptape.ai", output_artifact_namespace="WebResults", tool=WebScraper()),
        TextSummaryTask(input_artifact_namespace="WebResults", output_artifact_namespace="WebSummary", off_prompt=True),
        ImageGenerationTask(
            input_artifact_namespace="WebSummary",
            output_artifact_namespace="SummaryImage",
            image_generation_engine=ImageGenerationEngine(
                image_generation_driver=OpenAiDalleImageGenerationDriver(model="dall-e-3")
            ),
            off_prompt=True,
        ),
        ToolTask(
            "Save this artifact namespace {{ namespace }} from memory {{ memory}} into a file called griptape.png in the images directory",
            off_prompt=False,
            context={"namespace": "SummaryImage", "memory": "TaskMemory"},
            tool=FileManager(),
        ),
    ],
)

pipeline.run()
