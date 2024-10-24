from griptape.drivers import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask


def build_joke_teller() -> Agent:
    return Agent(
        rules=[
            Rule(
                value="You are very funny.",
            )
        ],
    )


def build_joke_rewriter() -> Agent:
    return Agent(
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
                create_structure=build_joke_teller,
            ),
        ),
        StructureRunTask(
            ("Rewrite this joke: {{ parent_output }}",),
            driver=LocalStructureRunDriver(
                create_structure=build_joke_rewriter,
            ),
        ),
    ]
)

joke_coordinator.run("Tell me a joke")
