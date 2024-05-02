## Overview
Structure Run Drivers are used to run Griptape Strucures hosted in other runtime environments.
When combined with the [StructureRunTask](../../reference/griptape/tasks/structure_run_task.md) or [GriptapeStructureRunClient](../../reference/griptape/tools/griptape_structure_run_client.md) you can run Structures in any runtime environment.

## Local Structure Run Driver

The [LocalStructureRunDriver](../../reference/griptape/drivers/structure-run/local-structure-run-driver.md) is used to run Griptape Structures in the same runtime environment as the code that is running the Structure.

```python
from griptape.drivers import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask

joke_teller = Agent(
    rules=[
        Rule(
            value="You are very funny.",
        )
    ],
)

joke_rewriter = Agent(
    rules=[
        Rule(
            value="You are the editor of a joke book. But you only speak in riddles",
        )
    ],
)

joke_coordinator = Pipeline(
    tasks=[
        StructureRunTask(
            driver=LocalStructureRunDriver(
                structure=joke_teller,
            ),
        ),
        StructureRunTask(
            "Rewrite this joke: {{ parent_output }}",
            driver=LocalStructureRunDriver(
                structure=joke_rewriter,
            ),
        ),
    ]
)

joke_coordinator.run("Tell me a joke")
```

## Griptape Cloud Structure Run Driver

The [GriptapeCloudStructureRunDriver](../../reference/griptape/drivers/structure-run/griptape-cloud-structure-run-driver.md) is used to run Griptape Structures in the Griptape Cloud.


```python
import os

from griptape.drivers import GriptapeCloudStructureRunDriver, LocalStructureRunDriver
from griptape.structures import Pipeline, Agent
from griptape.rules import Rule
from griptape.tasks import StructureRunTask

base_url = os.environ["GRIPTAPE_CLOUD_BASE_URL"]
api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
structure_id = os.environ["GRIPTAPE_CLOUD_STRUCTURE_ID"]


pipeline = Pipeline(
    tasks=[
        StructureRunTask(
            "Think of a question related to Retrieval Augmented Generation.",
            driver=LocalStructureRunDriver(
                structure=Agent(
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
            "{{ parent_output }}",
            driver=GriptapeCloudStructureRunDriver(
                base_url=base_url,
                api_key=api_key,
                structure_id=structure_id,
            ),
        ),
    ]
)

pipeline.run()
```
