import os

from griptape.drivers.structure_run.griptape_cloud import GriptapeCloudStructureRunDriver
from griptape.drivers.structure_run.local import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask

base_url = os.environ["GT_CLOUD_BASE_URL"]
api_key = os.environ["GT_CLOUD_API_KEY"]
structure_id = os.environ["GT_CLOUD_STRUCTURE_ID"]


pipeline = Pipeline(
    tasks=[
        StructureRunTask(
            ("Think of a question related to Retrieval Augmented Generation.",),
            structure_run_driver=LocalStructureRunDriver(
                create_structure=lambda: Agent(
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
            structure_run_driver=GriptapeCloudStructureRunDriver(
                base_url=base_url,
                api_key=api_key,
                structure_id=structure_id,
            ),
        ),
    ]
)

pipeline.run()
