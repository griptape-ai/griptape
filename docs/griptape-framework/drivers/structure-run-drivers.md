## Overview
Structure Run Drivers can be used to run Griptape Structures in a variety of runtime environments.
When combined with the [Structure Run Task](../../griptape-framework/structures/tasks.md#structure-run-task) or [Structure Run Client](../../griptape-tools/official-tools/structure-run-client.md) you can create complex, multi-agent pipelines that span multiple runtime environments.

## Local Structure Run Driver

The [LocalStructureRunDriver](../../reference/griptape/drivers/structure_run/local_structure_run_driver.md) is used to run Griptape Structures in the same runtime environment as the code that is running the Structure.

```python
from griptape.drivers import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask

def build_joke_teller():
    joke_teller = Agent(
        rules=[
            Rule(
                value="You are very funny.",
            )
        ],
    )

    return joke_teller

def build_joke_rewriter():
    joke_rewriter = Agent(
        rules=[
            Rule(
                value="You are the editor of a joke book. But you only speak in riddles",
            )
        ],
    )

    return joke_rewriter

joke_coordinator = Pipeline(
    tasks=[
        StructureRunTask(
            driver=LocalStructureRunDriver(
                structure_factory_fn=build_joke_teller,
            ),
        ),
        StructureRunTask(
            ("Rewrite this joke: {{ parent_output }}",),
            driver=LocalStructureRunDriver(
                structure_factory_fn=build_joke_rewriter,
            ),
        ),
    ]
)

joke_coordinator.run("Tell me a joke")
```

## Griptape Cloud Structure Run Driver

The [GriptapeCloudStructureRunDriver](../../reference/griptape/drivers/structure_run/griptape_cloud_structure_run_driver.md) is used to run Griptape Structures in the Griptape Cloud.


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
```
