from griptape.structures import Pipeline
from griptape.tools import WebScraper
from griptape.tasks import ToolTask, ImageGenerationTask, TextSummaryTask

pipeline = Pipeline(
    tasks=[
        ToolTask(
            "Scrape https://griptape.ai", off_prompt=True, output_artifact_namespace="WebResults", tool=WebScraper()
        ),
        TextSummaryTask(
            "Summarize the results", input_artifact_namespace="WebResults", output_artifact_namespace="WebSummary"
        ),
        ImageGenerationTask("Generate an image of the summary", input_artifact_namespace="WebSummary"),
    ]
)

pipeline.run()
