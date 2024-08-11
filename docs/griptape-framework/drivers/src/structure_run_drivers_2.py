import os

from griptape.drivers import GriptapeCloudStructureRunDriver, LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask

base_url = os.environ["GRIPTAPE_CLOUD_BASE_URL"]
api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
structure_id = os.environ["GRIPTAPE_CLOUD_STRUCTURE_ID"]


pipeline = Pipeline(
    tasks=[
        StructureRunTask(
            ("Think of a question related to Retrieval Augmented Generation.",),
            driver=LocalStructureRunDriver(
                structure_factory_fn=lambda: Agent(
                    rules=[
                        Rule(
                            value="You are an expert in Retrieval Augmented Generation.",
                        ),
                        Rule(
                            value="Only output your answer, no other information.",
                        ),
                    ]
                )
            ),
        ),
        StructureRunTask(
            ("{{ parent_output }}",),
            driver=GriptapeCloudStructureRunDriver(
                base_url=base_url,
                api_key=api_key,
                structure_id=structure_id,
            ),
        ),
    ]
)

pipeline.run()
